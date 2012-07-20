# -*- coding: utf-8 -*-

from flask import g, abort, flash, url_for, request, redirect
from coaster.views import load_models
from baseframe.forms import render_redirect, render_delete_sqla
from eventframe import app
from eventframe.views import NodeHandler, node_registry
from eventframe.forms import ContentForm, FragmentForm, RedirectForm, PublishForm, FunnelLinkForm
from eventframe.models import db, Website, Folder, Node, Page, Post, Fragment, Redirect, FunnelLink
from eventframe.views.login import lastuser
from eventframe.views.shared import render_form


class AutoFormHandler(NodeHandler):
    title_new = u"New node"
    title_edit = u"Edit node"

    def __init__(self, app, website, folder, node):
        super(AutoFormHandler, self).__init__(app, website, folder, node)
        self.form = self.make_form()

    def GET(self):
        return self.render_form()

    def POST(self):
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
            tabs=self.edit_tabs(), ajax=True)


class ContentHandler(AutoFormHandler):
    form_class = ContentForm

    def edit_tabs(self):
        if self.node:
            return [
                {'title': u"Edit", 'url': self.node.url_for('edit'), 'active': True},
                {'title': u"Publish", 'url': self.node.url_for('publish')},
                {'title': u"Unpublish", 'url': self.node.url_for('unpublish')},
                ]
        else:
            return []

    def make_form(self):
        # TODO: Add support for editing a specific revision
        if self.node:
            form = self.form_class(obj=self.node.last_revision())
            if request.method == 'GET':
                form.name.data = self.node.name
                form.properties.data = self.node.properties
            return form
        else:
            return self.form_class()

    def process_node(self):
        pass

    def process_form(self):
        if self.node is None:
            # Creating a new object
            self.node = self.model(folder=self.folder, user=g.user)
            db.session.add(self.node)
        # Name isn't in revision history, so name changes
        # are applied to the node. TODO: Move this into a separate
        # rename action
        self.node.name = self.form.name.data
        # Make a revision and apply changes to it
        revision = self.node.revise()
        # FIXME: Not all form fields are in the revision object. Don't
        # use populate_obj here
        self.form.populate_obj(revision)
        self.node.properties = self.form.properties.data
        self.process_node()
        if not self.node.title:
            # New object. Copy title from first revision
            self.node.title = revision.title
        elif not self.node.is_published:
            # There is no published version, so use title from the draft
            self.node.title = revision.title
        if not self.node.id and not self.node.name:
            self.node.make_name()
        db.session.commit()
        # FIXME: Say created when created
        flash(u"Edited node '%s'." % self.node.title, 'success')
        return render_redirect(url_for('folder', website=self.website.name, folder=self.folder.name), code=303)


class PageHandler(ContentHandler):
    model = Page
    title_new = u"New page"
    title_edit = u"Edit page"


class PostHandler(ContentHandler):
    model = Post
    title_new = u"New blog post"
    title_edit = u"Edit blog post"

    def make_form(self):
        form = super(PostHandler, self).make_form()
        if request.method == 'GET' and not self.node:
            form.template.data = 'post.html'
        return form


class FragmentHandler(ContentHandler):
    model = Fragment
    form_class = FragmentForm
    title_new = u"New page fragment"
    title_edit = u"Edit page fragment"


class FunnelLinkHandler(ContentHandler):
    model = FunnelLink
    form_class = FunnelLinkForm
    title_new = u"New funnel link"
    title_edit = u"Edit funnel link"

    def make_form(self):
        form = super(FunnelLinkHandler, self).make_form()
        if request.method == 'GET':
            if self.node:
                form.funnel_name.data = self.node.funnel_name
            else:
                form.template.data = 'funnel.html'
        return form

    def process_node(self):
        self.node.funnel_name = self.form.funnel_name.data


class RedirectHandler(AutoFormHandler):
    model = Redirect
    title_new = u"New redirect"
    title_edit = u"Edit redirect"

    def make_form(self):
        return RedirectForm(obj=self.node)

    def process_form(self):
        if self.node is None:
            self.node = self.model(folder=self.folder, user=g.user)
            db.session.add(self.node)
        self.form.populate_obj(self.node)
        db.session.commit()
        flash(u"Edited redirect '%s'." % self.node.title, 'success')
        return render_redirect(url_for('folder', website=self.website.name, folder=self.folder.name), code=303)


class RedirectViewHandler(NodeHandler):
    def GET(self):
        return redirect(self.node.redirect_url)

node_registry.register(Page, PageHandler, render=True)
node_registry.register(Post, PostHandler, render=True)
node_registry.register(Fragment, FragmentHandler, render=False)
node_registry.register(Redirect, RedirectHandler, view_handler=RedirectViewHandler, render=False)
node_registry.register(FunnelLink, FunnelLinkHandler, render=True)


# --- Routes ------------------------------------------------------------------

@app.route('/<website>/<folder>/_new/<type>', methods=['GET', 'POST'])
@app.route('/<website>/_root/_new/<type>', defaults={'folder': u''}, methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder'),
    kwargs=True
    )
def node_new(website, folder, kwargs):
    g.website = website
    g.folder = folder
    type = kwargs['type']
    if type not in node_registry:
        abort(404)
    record = node_registry[type]
    handler_class = record.edit_handler
    if handler_class is None:
        abort(404)
    handler = handler_class(app, website, folder, None)

    if request.method == 'GET':
        return handler.GET()
    elif request.method == 'POST':
        return handler.POST()
    else:
        abort(405)


@app.route('/<website>/<folder>/<node>/_edit', methods=['GET', 'POST'])
@app.route('/<website>/_root/<node>/_edit', defaults={'folder': u''}, methods=['GET', 'POST'])
@app.route('/<website>/<folder>/_index/_edit', defaults={'node': u''}, methods=['GET', 'POST'])
@app.route('/<website>/_root/_index/_edit', defaults={'folder': u'', 'node': u''}, methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder'),
    (Node, {'name': 'node', 'folder': 'folder'}, 'node')
    )
def node_edit(website, folder, node):
    g.website = website
    g.folder = folder
    record = node_registry[node.type]
    handler_class = record.edit_handler
    if handler_class is None:
        abort(404)
    handler = handler_class(app, website, folder, node)

    if request.method == 'GET':
        return handler.GET()
    elif request.method == 'POST':
        return handler.POST()
    else:
        abort(405)


@app.route('/<website>/<folder>/<node>/_delete', methods=['GET', 'POST'])
@app.route('/<website>/_root/<node>/_delete', defaults={'folder': u''}, methods=['GET', 'POST'])
@app.route('/<website>/<folder>/_index/_delete', defaults={'node': u''}, methods=['GET', 'POST'])
@app.route('/<website>/_root/_index/_delete', defaults={'folder': u'', 'node': u''}, methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder'),
    (Node, {'name': 'node', 'folder': 'folder'}, 'node')
    )
def node_delete(website, folder, node):
    g.website = website
    g.folder = folder
    return render_delete_sqla(node, db, title=u"Confirm delete",
        message=u"Delete '%s'? This is permanent. There is no undo." % node.title,
        success=u"You have deleted '%s'." % node.title,
        next=url_for('folder', website=website.name, folder=folder.name))


# Temporary publish handler that needs to be rolled into the edit handler
@app.route('/<website>/<folder>/<node>/_publish', methods=['GET', 'POST'])
@app.route('/<website>/_root/<node>/_publish', defaults={'folder': u''}, methods=['GET', 'POST'])
@app.route('/<website>/<folder>/_index/_publish', defaults={'node': u''}, methods=['GET', 'POST'])
@app.route('/<website>/_root/_index/_publish', defaults={'folder': u'', 'node': u''}, methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder'),
    (Node, {'name': 'node', 'folder': 'folder'}, 'node')
    )
def node_publish(website, folder, node):
    g.website = website
    g.folder = folder
    if not (hasattr(node, 'publish') and callable(node.publish)):
        abort(404)
    form = PublishForm(obj=node)
    if form.validate_on_submit():
        node.publish()
        db.session.commit()
        flash(u"Published '%s'" % node.title, 'success')
        return render_redirect(url_for('folder', website=folder.website.name, folder=folder.name), code=303)
    return render_form(form=form, title="Publish node", submit=u"Publish",
            cancel_url=url_for('folder', website=folder.website.name, folder=folder.name))


# Temporary publish handler that needs to be rolled into the edit handler
@app.route('/<website>/<folder>/<node>/_unpublish', methods=['GET', 'POST'])
@app.route('/<website>/_root/<node>/_unpublish', defaults={'folder': u''}, methods=['GET', 'POST'])
@app.route('/<website>/<folder>/_index/_unpublish', defaults={'node': u''}, methods=['GET', 'POST'])
@app.route('/<website>/_root/_index/_unpublish', defaults={'folder': u'', 'node': u''}, methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder'),
    (Node, {'name': 'node', 'folder': 'folder'}, 'node')
    )
def node_unpublish(website, folder, node):
    g.website = website
    g.folder = folder
    if not (hasattr(node, 'unpublish') and callable(node.unpublish)):
        abort(404)
    form = PublishForm(obj=node)
    if form.validate_on_submit():
        node.unpublish()
        db.session.commit()
        flash(u"Unpublished '%s'" % node.title, 'success')
        return render_redirect(url_for('folder', website=folder.website.name, folder=folder.name), code=303)
    return render_form(form=form, title="Unpublish node", submit=u"Unpublish",
            cancel_url=url_for('folder', website=folder.website.name, folder=folder.name))
