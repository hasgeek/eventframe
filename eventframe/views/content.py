# -*- coding: utf-8 -*-

from flask import g, abort, flash, url_for, request
from coaster.views import load_models
from baseframe.forms import render_redirect, render_delete_sqla
from eventframe import app
from eventframe.models import db, Website, Folder, Node
from eventframe.forms import ConfirmForm
from eventframe.nodes import node_registry, render_form
from eventframe.views.login import lastuser


# --- Routes ------------------------------------------------------------------

@app.route('/<website>/<folder>/_new/<type>', methods=['GET', 'POST'])
@app.route('/<website>/_root/_new/<type>', defaults={'folder': ''}, methods=['GET', 'POST'])
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
@app.route('/<website>/_root/<node>/_edit', defaults={'folder': ''}, methods=['GET', 'POST'])
@app.route('/<website>/<folder>/_index/_edit', defaults={'node': ''}, methods=['GET', 'POST'])
@app.route('/<website>/_root/_index/_edit', defaults={'folder': '', 'node': ''}, methods=['GET', 'POST'])
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


@app.route('/<website>/<folder>/<node>/do/<action>', methods=['GET', 'POST'])
@app.route('/<website>/_root/<node>/do/<action>', defaults={'folder': ''}, methods=['GET', 'POST'])
@app.route('/<website>/<folder>/_index/do/<action>', defaults={'node': ''}, methods=['GET', 'POST'])
@app.route('/<website>/_root/_index/do/<action>', defaults={'folder': '', 'node': ''}, methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder'),
    (Node, {'name': 'node', 'folder': 'folder'}, 'node'),
    kwargs=True,
    )
def node_action(website, folder, node, kwargs):
    action = kwargs['action']
    g.website = website
    g.folder = folder
    record = node_registry[node.type]
    handler_class = record.edit_handler
    if handler_class is None:
        abort(404)
    handler = handler_class(app, website, folder, node)
    if action not in handler.actions:
        abort(404)
    if not hasattr(handler, action):
        abort(404)
    method = getattr(handler, action)
    if not callable(method):
        abort(404)
    return method()


@app.route('/<website>/<folder>/<node>/_delete', methods=['GET', 'POST'])
@app.route('/<website>/_root/<node>/_delete', defaults={'folder': ''}, methods=['GET', 'POST'])
@app.route('/<website>/<folder>/_index/_delete', defaults={'node': ''}, methods=['GET', 'POST'])
@app.route('/<website>/_root/_index/_delete', defaults={'folder': '', 'node': ''}, methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder'),
    (Node, {'name': 'node', 'folder': 'folder'}, 'node')
    )
def node_delete(website, folder, node):
    g.website = website
    g.folder = folder
    return render_delete_sqla(node, db, title="Confirm delete",
        message="Delete '%s'? This is permanent. There is no undo." % node.title,
        success="You have deleted '%s'." % node.title,
        next=url_for('folder', website=website.name, folder=folder.name))


# Temporary publish handler that needs to be rolled into the edit handler
@app.route('/<website>/<folder>/<node>/_publish', methods=['GET', 'POST'])
@app.route('/<website>/_root/<node>/_publish', defaults={'folder': ''}, methods=['GET', 'POST'])
@app.route('/<website>/<folder>/_index/_publish', defaults={'node': ''}, methods=['GET', 'POST'])
@app.route('/<website>/_root/_index/_publish', defaults={'folder': '', 'node': ''}, methods=['GET', 'POST'])
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
    form = ConfirmForm(obj=node)
    if form.validate_on_submit():
        node.publish()
        db.session.commit()
        flash("Published '%s'" % node.title, 'success')
        return render_redirect(url_for('folder', website=folder.website.name, folder=folder.name), code=303)
    return render_form(form=form, title="Publish node", submit="Publish",
        cancel_url=url_for('folder', website=folder.website.name, folder=folder.name),
        node=node)


# Temporary publish handler that needs to be rolled into the edit handler
@app.route('/<website>/<folder>/<node>/_unpublish', methods=['GET', 'POST'])
@app.route('/<website>/_root/<node>/_unpublish', defaults={'folder': ''}, methods=['GET', 'POST'])
@app.route('/<website>/<folder>/_index/_unpublish', defaults={'node': ''}, methods=['GET', 'POST'])
@app.route('/<website>/_root/_index/_unpublish', defaults={'folder': '', 'node': ''}, methods=['GET', 'POST'])
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
    form = ConfirmForm(obj=node)
    if form.validate_on_submit():
        node.unpublish()
        db.session.commit()
        flash("Unpublished '%s'" % node.title, 'success')
        return render_redirect(url_for('folder', website=folder.website.name, folder=folder.name), code=303)
    return render_form(form=form, title="Unpublish node", submit="Unpublish",
        cancel_url=url_for('folder', website=folder.website.name, folder=folder.name),
        node=node)
