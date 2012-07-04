# -*- coding: utf-8 -*-

from flask import abort

# Create a node registry
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


class NodeHandler(object):
    form = None
    model = None

    def __init__(self, app, website, folder, node):
        self.app = app
        self.website = website
        self.folder = folder
        self.node = node

    # Called if the node is directly called
    def GET(self, *args, **kwargs):
        abort(405)

    # Called if the node is directly called
    def POST(self, *args, **kwargs):
        abort(405)


class _RegistryItem(object):
    pass


class NodeRegistry(OrderedDict):

    def register(self, model, edit_handler, edit_url_map=None, view_handler=None, view_url_map=None, render=False):
        item = _RegistryItem()
        item.model = model
        item.name = model.__mapper_args__['polymorphic_identity']
        item.title = model.__title__
        item.edit_handler = edit_handler
        item.edit_url_map = edit_url_map
        item.view_handler = view_handler
        item.view_url_map = view_url_map
        item.render = render

        self[item.name] = item

node_registry = NodeRegistry()

# Import views

import eventframe.views.index
import eventframe.views.login
import eventframe.views.website
import eventframe.views.eventlogin
import eventframe.views.admin
import eventframe.views.context
import eventframe.views.content
import eventframe.views.list
import eventframe.views.map
import eventframe.views.errorhandlers
