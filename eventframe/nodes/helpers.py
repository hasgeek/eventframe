# -*- coding: utf-8 -*-

from werkzeug.exceptions import NotFound
from functools import wraps
from flask import g, abort, current_app, request, render_template, url_for
import wtforms
from eventframe.models import Hostname

__all__ = ['NodeHandler', 'AutoFormHandler', 'node_registry', 'render_form', 'stream_template', 'get_website']

# Create a node registry
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


class NodeHandler(object):
    form = None
    model = None
    actions = []

    def __init__(self, app, website, folder, node):
        self.app = app
        self.website = website
        self.folder = folder
        self.node = node
        self.action = 'edit'

    # Called if the node is directly called
    def GET(self, *args, **kwargs):
        abort(405)

    # Called if the node is directly called
    def POST(self, *args, **kwargs):
        abort(405)


class AutoFormHandler(NodeHandler):
    title_new = u"New node"
    title_edit = u"Edit node"

    def __init__(self, app, website, folder, node):
        super(AutoFormHandler, self).__init__(app, website, folder, node)

    def GET(self):
        self.form = self.make_form()
        return self.render_form()

    def POST(self):
        self.form = self.make_form()
        if self.form.validate_on_submit():
            return self.process_form()
        return self.render_form()

    def edit_tabs(self):
        return []

    def make_form(self):
        raise NotImplementedError

    def process_form(self):
        raise NotImplementedError

    def render_form(self):
        return render_form(form=self.form, title=self.title_edit if self.node else self.title_new, submit=u"Save",
            cancel_url=url_for('folder', website=self.website.name, folder=self.folder.name),
            tabs=self.edit_tabs(), node=self.node, ajax=False)


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


def render_form(form, title, message='', formid='form', submit=u"Submit", cancel_url=None, tabs=[], node=None, ajax=False):
    multipart = False
    for field in form:
        if isinstance(field.widget, wtforms.widgets.FileInput):
            multipart = True
    if request.is_xhr and ajax:
        return render_template('baseframe/ajaxform.html', form=form, title=title,
            message=message, formid=formid, submit=submit,
            cancel_url=cancel_url, multipart=multipart, node=node)
    else:
        return render_template('autoform.html', form=form, title=title,
            message=message, formid=formid, submit=submit,
            cancel_url=cancel_url, ajax=ajax, multipart=multipart,
            tabs=tabs, node=node)


def stream_template(template_name, **context):
    current_app.update_template_context(context)
    t = current_app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.disable_buffering()
    return rv

node_registry = NodeRegistry()
