# -*- coding: utf-8 -*-

import os.path
from werkzeug.exceptions import NotFound
from flask import g, request, abort, redirect, send_file
from flask.ext.themes import get_theme, render_theme_template
from baseframe import favicon as baseframe_favicon
from eventframe import eventapp
from eventframe.nodes import node_registry, get_website
from eventframe.models import Folder, Node


@eventapp.route('/')
def index():
    return node(folder=u'', node=u'')


@eventapp.route('/favicon.ico')
@get_website
def favicon(website):
    theme = get_theme(website.theme)
    favicon = theme.options.get('favicon')
    if favicon:
        return send_file(os.path.join(theme.static_path, favicon))
    else:
        return baseframe_favicon()


# TODO: Deprecate this and move to path_handler
@eventapp.route('/<folder>/<node>')
@get_website
def node(website, folder, node):
    folderob = Folder.query.filter_by(name=folder, website=website).first()
    if folderob is None:
        # Are we handling a /node/custom_url case?
        folderob = Folder.query.filter_by(name=u'', website=website).first_or_404()
        nodeob = Node.query.filter_by(name=folder, folder=folderob).first_or_404()
        # The node exists. Let the path handler figure out what to do with it
        return path_handler(path=u'/' + nodeob.name + u'/' + node)
    else:
        nodeob = Node.query.filter_by(name=node, folder=folderob).first_or_404()

    # For the context processor to pick up theme for this request
    # and for the nodehelper to know the current folder
    g.folder = folderob
    if node_registry[nodeob.type].view_handler is not None:
        # This node type is capable of rendering itself
        return node_registry[nodeob.type].view_handler(eventapp, folderob.website, folderob, nodeob).GET()
    elif node_registry[nodeob.type].render:
        theme = get_theme(folderob.theme)
        return render_theme_template(theme, nodeob.template,
            website=folderob.website, folder=folderob, title=nodeob.title, node=nodeob, _fallback=False)
    else:
        abort(404)  # We don't know how to render anything else


# TODO: Deprecate this and move to path_handler
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
    pathcomponents = []
    if components[0] == u'':
        # We had a / prefix. Discard it.
        components.pop(0)
    if len(components) > 2 and components[-1] == u'':
        # We got a trailing slash and it's not a folder. Pop it.
        components.pop(-1)
        return redirect(request.script_root + u'/' + u'/'.join(components))
    # Now what do we have?
    # A: /
    # B: /folder/ or /node/
    # C: /folder/node
    # D: /node/custom where custom can have many segments
    # E: /folder/node/custom where custom can have many segments
    if len(components) == 0:
        # A: Render (root)/(index) [both named '']
        folder = Folder.query.filter_by(website=website, name=u'').first_or_404()
        node = Node.query.filter_by(folder=folder, name=u'').first_or_404()
    elif len(components) == 1:
        # B: Could be a folder or node:
        folder = Folder.query.filter_by(website=website, name=components[0]).first()
        if folder is not None:
            node = Node.query.filter_by(folder=folder, name=u'').first_or_404()
        else:
            folder = Folder.query.filter_by(website=website, name=u'').first_or_404()
            node = Node.query.filter_by(folder=folder, name=components[0]).first_or_404()
    else:
        folder = Folder.query.filter_by(website=website, name=components[0]).first()
        if folder is not None:
            # C: folder/node or E: folder/node/custom
            node = Node.query.filter_by(folder=folder, name=components[1]).first_or_404()
            pathcomponents = components[2:]
        else:
            # D: node/custom
            folder = Folder.query.filter_by(website=website, name=u'').first_or_404()
            node = Node.query.filter_by(folder=folder, name=components[0]).first_or_404()
            pathcomponents = components[1:]

    # For the context processor to pick up theme for this request
    # and for the nodehelper to know the current folder
    g.folder = folder
    if len(pathcomponents) == 0 and request.method == 'POST':
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
                path_info='/'.join(pathcomponents))
