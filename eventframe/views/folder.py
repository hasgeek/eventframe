# -*- coding: utf-8 -*-

"""
Admin views
"""

from coaster.utils import parse_isoformat, buid, make_name
from coaster.views import load_model, load_models
from flask import g, flash, url_for, render_template, request, Response, session
import simplejson as json
from flask_themes import get_themes_list
from baseframe.forms import render_redirect, render_delete_sqla

from eventframe import app
from eventframe.models import db, User, Website, Folder, Node
from eventframe.forms import WebsiteForm, FolderForm, ImportForm
from eventframe.nodes import node_registry, render_form
from eventframe.views.login import lastuser


@app.route('/_new', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
def website_new():
    form = WebsiteForm()
    themes = [(t.identifier, t.name) for t in get_themes_list()]
    form.theme.choices = themes
    if form.validate_on_submit():
        website = Website()
        form.populate_obj(website)
        db.session.add(website)
        db.session.commit()
        return render_redirect(url_for('website', website=website.name), code=303)
    return render_form(form=form, title=u"New website", submit=u"Create",
        cancel_url=url_for('index'), ajax=True)


@app.route('/<website>/_edit', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Website, {'name': 'website'}, 'website')
def website_edit(website):
    g.website = website
    form = WebsiteForm(obj=website)
    themes = [(t.identifier, t.name) for t in get_themes_list()]
    form.theme.choices = themes
    if form.validate_on_submit():
        form.populate_obj(website)
        db.session.commit()
        return render_redirect(url_for('website', website=website.name), code=303)
    return render_form(form=form, title=u"Edit website", submit=u"Save",
        cancel_url=url_for('website', website=website.name), ajax=True)


@app.route('/<website>/_delete', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Website, {'name': 'website'}, 'website')
def website_delete(website):
    g.website = website
    return render_delete_sqla(website, db, title=u"Confirm delete",
        message=u"Delete website '%s'? This will also permanently remove all "
            "pages associated with the website. There is no undo." % website.title,
        success=u"You have deleted website '%s'." % website.title,
        next=url_for('index'))


@app.route('/<website>/_new', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Website, {'name': 'website'}, 'website')
def folder_new(website):
    g.website = website
    form = FolderForm()
    themes = [('', 'Website Default')] + [(t.identifier, t.name) for t in get_themes_list()]
    form.theme.choices = themes
    if form.validate_on_submit():
        folder = Folder(website=website)
        form.populate_obj(folder)
        db.session.add(folder)
        db.session.commit()
        return render_redirect(url_for('folder', website=website.name, folder=folder.name), code=303)
    return render_form(form=form, title=u"New folder", submit=u"Create",
        cancel_url=url_for('website', website=website.name), ajax=True)


@app.route('/<website>/<folder>/_edit', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder')
    )
def folder_edit(website, folder):
    g.website = website
    g.folder = folder
    form = FolderForm(obj=folder)
    if request.method == 'GET':
        form.theme.data = folder._theme
    themes = [('', 'Website Default')] + [(t.identifier, t.name) for t in get_themes_list()]
    form.theme.choices = themes
    if form.validate_on_submit():
        form.populate_obj(folder)
        db.session.commit()
        return render_redirect(url_for('folder', website=website.name, folder=folder.name), code=303)
    return render_form(form=form, title=u"Edit folder", submit=u"Save",
        cancel_url=url_for('folder', website=website.name, folder=folder.name), ajax=True)


def clipboard_paste(folder, nodeids, action):
    nodes = Node.query.filter(Node.uuid.in_(nodeids)).all()
    returnids = []
    nameconflicts = dict(db.session.query(Node.name, Node.id).filter_by(folder=folder).all())
    for node in nodes:
        if action == 'cut':
            # Move the node
            node.folder = folder
        elif action == 'copy':
            # Copy and paste data
            data = node.as_json()
            with db.session.no_autoflush:
                newnode = node.__class__(folder=folder)
                newnode.user = g.user
                newnode.import_from(data)
                newnode.import_from_internal(data)
                newnode.uuid = buid()  # import_from will copy the UUID. Regenerate it.
            node = newnode  # For the namecheck below
        # If the name conflicts, give it a new name. maxlength=250 from coaster.sqlalchemy
        returnids.append(node.uuid)
        if node.name in nameconflicts:
            if node.id != nameconflicts[node.name]:
                node.name = make_name(node.name, maxlength=250, checkused=lambda n: n in nameconflicts)
    return returnids


@app.route('/<website>/<folder>', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder')
    )
def folder(website, folder):
    g.website = website
    g.folder = folder
    highlight = set()
    cutlist = set()
    if request.method == 'POST' and 'action' in request.form:
        action = request.form['action']
        if action in ['cut', 'copy']:
            session['clipboard'] = request.form.getlist('nodeid')
            session['clipboard_type'] = action
            if action == 'cut':
                cutlist.update(request.form.getlist('nodeid'))
        elif action == 'paste':
            if 'clipboard' in session:
                clip_action = session.get('clipboard_type')
                if clip_action == 'cut':
                    highlight.update(clipboard_paste(folder, session['clipboard'], clip_action))
                    db.session.commit()
                elif clip_action == 'copy':
                    highlight.update(clipboard_paste(folder, session['clipboard'], clip_action))
                    db.session.commit()
                else:
                    flash(u"Unknown clipboard action requested", "error")
            else:
                flash(u"Nothing to paste", "error")
            session.pop('clipboard', None)
            session.pop('clipboard_type', None)
        elif action == 'delete':
            # Delete items
            nodes = Node.query.filter(Node.uuid.in_(request.form.getlist('nodeid'))).all()
            for node in nodes:
                db.session.delete(node)
            if len(nodes) == 1:
                flash(u"“%s” has been deleted" % nodes[0].title, "success")
            else:
                flash(u"%d items have been deleted" % len(nodes), "success")
            db.session.commit()
        elif action == 'rename':
            flash("Rename hasn't been implemented yet", "info")

    return render_template('folder.html', website=website, folder=folder,
        node_registry=node_registry, importform=ImportForm(),
        highlight=highlight, cutlist=cutlist)


@app.route('/<website>/', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
def website(website):
    g.website = website
    return folder(website=website, folder='')


@app.route('/<website>/<folder>/_delete', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder')
    )
def folder_delete(website, folder):
    g.website = website
    g.folder = folder
    return render_delete_sqla(folder, db, title=u"Confirm delete",
        message=u"Delete folder '%s'? This will also permanently remove all "
            "pages in this folder. There is no undo." % folder.name,
        success=u"You have deleted folder '%s'." % folder.name,
        next=url_for('website', website=website.name))


@app.route('/<website>/<folder>/_export')
@app.route('/<website>/_root/_export', defaults={'folder': u''})
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder')
    )
def folder_export(website, folder):
    response = Response(
        json.dumps({
                'website': website.name,
                'folder': folder.name,
                'nodes': [node.as_json() for node in folder.nodes]},
            use_decimal=True, sort_keys=True, indent=4),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename="%s-%s.json"' % (
            website.name, folder.name)})
    return response


@app.route('/<website>/<folder>/_import', methods=['GET', 'POST'])
@app.route('/<website>/_root/_import', defaults={'folder': u''}, methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder')
    )
def folder_import(website, folder):
    g.website = website
    g.folder = folder
    import_count = 0
    create_count = 0
    form = ImportForm()
    internal_imports = []
    if form.validate_on_submit():
        data = json.loads(request.files['import_file'].getvalue(), use_decimal=True)
        for inode in data['nodes']:
            mtime = parse_isoformat(inode.get('revision_updated_at', inode['updated_at']))
            node = Node.query.filter_by(folder=folder, uuid=inode['uuid']).first()
            with db.session.no_autoflush:
                if node is None:
                    nreg = node_registry.get(inode['type'])
                    if nreg is None:
                        flash("Could not import node of unknown type '%s'" % inode['type'], "error")
                        continue
                    node = nreg.model(folder=folder)
                    user = User.query.filter_by(userid=inode['userid']).first()
                    node.user = user or g.user
                    db.session.add(node)
                    create_count += 1
                else:
                    if form.import_updated.data and mtime <= node.updated_at:
                        continue
                node.import_from(inode)
            internal_imports.append(inode)
            import_count += 1
        db.session.commit()
        # Second pass for internal data of nodes
        for inode in internal_imports:
            node = Node.query.filter_by(folder=folder, uuid=inode['uuid']).first()
            node.import_from_internal(inode)
        db.session.commit()
        flash("%d nodes were imported and %d new nodes were created" % (import_count, create_count), "success")
        return render_redirect(url_for('folder', website=website.name, folder=folder.name), code=303)
    return render_form(form=form, title=u"Import to folder", submit=u"Upload",
        cancel_url=url_for('folder', website=website.name, folder=folder.name))
