# -*- coding: utf-8 -*-

# Create a node registry
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


class NodeHandler(object):
    form = None
    model = None

    def make_form(self, folder, node):
        raise NotImplementedError

    def process_form(self, folder, node, form):
        raise NotImplementedError

    def render_form(self, folder, node, form):
        raise NotImplementedError


class _RegistryItem(object):
    pass


class NodeRegistry(OrderedDict):

    def register(self, model, handler, render=False):
        item = _RegistryItem()
        item.model = model
        item.name = model.__mapper_args__['polymorphic_identity']
        item.title = model.__title__
        item.handler = handler
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
