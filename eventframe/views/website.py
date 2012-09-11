# -*- coding: utf-8 -*-

from werkzeug.exceptions import NotFound
from flask import g, request, abort, redirect
from flask.ext.themes import get_theme, render_theme_template
from coaster.views import load_models
from eventframe import eventapp
from eventframe.nodes import node_registry, get_website
from eventframe.models import Folder, Node


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
    # For the context processor to pick up theme for this request
    # and for the nodehelper to know the current folder
    g.folder = folder
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


@eventapp.route('/<path:path>', methods=['GET', 'POST'])
@get_website
def path_handler(website, path):
    """Handles paths for nodes with internal items."""
    components = path.split('/')
    if components[0] == u'':
        # We had a / prefix. Discard it.
        components.pop(0)
    if len(components) > 2 and components[-1] == u'':
        # We got a trailing slash and it's not a folder. Pop it.
        components.pop(-1)
        return redirect(request.script_root + u'/'.join(components))
    # Now what do we have?
    # A: /
    # B: /folder/ or /node/
    # C: /folder/node
    if len(components) == 0:
        # Render (root)/(index) [both named '']
        folder = Folder.query.filter_by(website=website, name=u'').first_or_404()
        node = Node.query.filter_by(folder=folder, name=u'').first_or_404()
    elif len(components) == 1:
        # Could be a folder or node:
        folder = Folder.query.filter_by(website=website, name=components[0]).first()
        if folder is not None:
            node = Node.query.filter_by(folder=folder, name=u'').first_or_404()
        else:
            folder = Folder.query.filter_by(website=website, name=u'').first_or_404()
            node = Node.query.filter_by(folder=folder, name=components[0]).first_or_404()
    else:
        folder = Folder.query.filter_by(website=website, name=components[0]).first_or_404()
        node = Node.query.filter_by(folder=folder, name=components[1]).first_or_404()
    if len(components) <= 2 and request.method == 'POST':
        # This is a POST request on the node. Does it take POST?
        if node_registry[node.type].view_handler is None:
            abort(405)
        else:
            return node_registry[node.type].view_handler(eventapp, website, folder, node).POST()
    else:
        # Now we come to the core of it: find a node and see if has a url_map and view handler.
        # Delegate if yes, raise a 404 if no. We can only get here with named folders and nodes.
        if node_registry[node.type].view_url_map is None or node_registry[node.type].view_handler is None:
            abort(404)
        else:
            urls = node_registry[node.type].view_url_map.bind_to_environ(request)
            view_handler = node_registry[node.type].view_handler(eventapp, website, folder, node)
            return urls.dispatch(lambda e, v: getattr(view_handler, e)(**v),
                path_info='/'.join(components[2:]))
