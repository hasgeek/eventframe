# -*- coding: utf-8 -*-

from functools import wraps
from datetime import datetime
from werkzeug.exceptions import NotFound
from flask import g, request, url_for, Response, abort, redirect
from flask.ext.themes import get_theme, render_theme_template
from coaster.views import load_model, load_models
from eventframe import eventapp
from eventframe.views import node_registry
from eventframe.models import db, Hostname, Folder, Node, Post, Redirect


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
    if isinstance(node, Redirect):
        return redirect(node.redirect_url)
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
    return Post.query.filter_by(is_published=True).order_by('post.published_at')


def rootfeed(website):
    folder_ids = [i[0] for i in db.session.query(Folder.id).filter_by(website=website).all()]
    return feedquery().filter(Node.folder_id.in_(folder_ids)).all()


def folderfeed(folder):
    return feedquery().filter(Node.folder == folder).all()


@eventapp.route('/feed')
@get_website
def feed(website):
    theme = get_theme(website.theme)
    posts = rootfeed(website)
    if posts:
        updated = posts[0].published_at.isoformat() + 'Z'
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
