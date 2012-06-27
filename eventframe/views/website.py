# -*- coding: utf-8 -*-

from functools import wraps
from datetime import datetime
from werkzeug.exceptions import NotFound
from flask import g, request, url_for, Response, abort, redirect
from flask.ext.themes import get_theme, render_theme_template
from coaster.views import load_model, load_models
from eventframe import eventapp
from eventframe.views import node_registry
from eventframe.models import db, Hostname, Folder, Node, Post


def get_website(f):
    @wraps(f)
    def decorated_function(**kwargs):
        website = g.website if hasattr(g, 'website') else None
        if website is None:
            httphost = request.environ['HTTP_HOST']
            if ':' in httphost:
                httphost = httphost.split(':', 1)[0]
            hostname = Hostname.query.filter_by(name=httphost).first()
            if not hostname:
                return NotFound()
            else:
                g.website = hostname.website
        return f(website=g.website, **kwargs)
    return decorated_function


@eventapp.route('/')
def index():
    return node(folder=u'', node=u'')


@eventapp.route('/<folder>/<node>')
@get_website
@load_models(
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder'),
    (Node, {'name': 'node', 'folder': 'folder'}, 'node')
    )
def node(folder, node):
    g.folder = folder  # For the context processor to pick up theme for this request
    if node_registry[node.type].view_handler is not None:
        # This node type is capable of rendering itself
        return node_registry[node.type].view_handler(eventapp, folder.website, folder, node).GET()
    elif node_registry[node.type].render:
        theme = get_theme(folder.theme)
        return render_theme_template(theme, node.template,
            website=folder.website, folder=folder, title=node.title, node=node, _fallback=False)
    else:
        abort(404)  # We don't know how to render anything else


@eventapp.route('/<folder>/')
@get_website
def folder(website, folder):
    try:
        return node(folder=folder, node=u'')
    except NotFound:
        return node(folder=u'', node=folder)


def feedquery():
    return Post.query.filter_by(is_published=True).order_by(db.desc('node.published_at'))


def rootfeed(website, limit=20):
    folder_ids = [i[0] for i in db.session.query(Folder.id).filter_by(website=website).all()]
    query = feedquery().filter(Node.folder_id.in_(folder_ids))
    if limit:
        query = query.limit(limit)
    return query.all()


def folderfeed(folder, limit=20):
    query = feedquery().filter(Node.folder == folder)
    if limit:
        query = query.limit(limit)
    return query.all()


@eventapp.route('/feed')
@get_website
def feed(website):
    theme = get_theme(website.theme)
    posts = rootfeed(website)
    if posts:
        updated = max(posts[0].revisions.published.updated_at, posts[0].published_at).isoformat() + 'Z'
    else:
        updated = datetime.utcnow().isoformat() + 'Z'
    return Response(render_theme_template(theme, 'feed.xml',
            feedid=url_for('index', _external=True),
            website=website, title=website.title, posts=posts, updated=updated),
        content_type='application/atom+xml; charset=utf-8')


@eventapp.route('/<folder>/feed')
@get_website
@load_model(Folder, {'name': 'folder', 'website': 'website'}, 'folder')
def folder_feed(folder):
    theme = get_theme(folder.theme)
    posts = folderfeed(folder)
    if posts:
        updated = posts[0].published_at.isoformat() + 'Z'
    else:
        updated = datetime.utcnow().isoformat() + 'Z'
    return Response(render_theme_template(theme, 'feed.xml',
            feedid=url_for('folder', folder=folder.name),
            website=folder.website, title=u"%s — %s" % (folder.title, folder.website.title), posts=posts, updated=updated),
        content_type='application/atom+xml; charset=utf-8')


@eventapp.route('/<path:path>', methods=['GET', 'POST'])
@get_website
def path_handler(website, path):
    """Handles paths for nodes with internal items."""
    components = path.split('/')
    if len(components) > 2 and components[-1] == u'':
        # We got a trailing slash and it's not a folder. Pop it.
        components.pop(-1)
        return redirect(u'/'.join(components))
    # The first part of components is always blank to indicate the leading /
    components.pop(0)
    # Now what do we have?
    # A: /
    # B: /folder/ or /node/
    # C: /folder/node
    if len(components) == 0:
        folder = Folder.query.filter_by(website=website, name=u'').first_or_404()
        node = Node.query.filter_by(folder=folder, name=u'').first_or_404()
    elif len(components) == 1:
        # Could be folder or node:
        folder = Folder.query.filter_by(website=website, name=components[0]).first()
        if folder is not None:
            node = Node.query.filter_by(folder=folder, name=u'').first_or_404()
        else:
            folder = Folder.query.filter_by(website=website, name=u'').first_or_404()
            node = Node.query.filter_by(folder=folder, name=u'').first_or_404()
    else:
        folder = Folder.query.filter_by(website=website, name=components[0]).first_or_404()
        node = Node.query.filter_by(folder=folder, node=components[1]).first_or_404()
    if len(components) <= 2 and request.method == 'POST':
        # This is a POST request on the node. Does it take POST?
        if node_registry[node.type].view_handler is None:
            abort(405)
        else:
            return node_registry[node.type].view_handler(eventapp, website, folder, node).POST()
    else:
        # Now we come to the core of it: find a node and see if has a url_map and view handler.
        # Delegate if yes, raise a 404 if no.
        if node_registry[node.type].view_url_map is None or node_registry[node.type].view_handler is None:
            abort(404)
        else:
            urls = node_registry[node.type].view_url_map.bind_to_environ(request)
            return urls.dispatch(lambda e, v: getattr(node_registry[node.type].view_handler, 'e')(**v))
