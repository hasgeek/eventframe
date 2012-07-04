# -*- coding: utf-8 -*-

"""
Admin views
"""

from coaster import parse_isoformat
from coaster.views import load_model, load_models
from flask import g, flash, url_for, render_template, request, Response, json
from flask.ext.themes import get_themes_list
from baseframe.forms import render_form, render_redirect, render_delete_sqla

from eventframe import app, eventapp
from eventframe.models import db, User, Website, Folder, Node
from eventframe.forms import WebsiteForm, FolderForm, ImportForm
from eventframe.views import node_registry
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
    return render_delete_sqla(website, db, title=u"Confirm delete",
        message=u"Delete website '%s'? This will also permanently remove all "
            "pages associated with the website. There is no undo." % website.title,
        success=u"You have deleted website '%s'." % website.title,
        next=url_for('index'))


@app.route('/<website>/_new', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Website, {'name': 'website'}, 'website')
def folder_new(website):
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


@app.route('/<website>/<folder>', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder')
    )
def folder(website, folder):
    return render_template('folder.html', website=website, folder=folder,
        node_registry=node_registry, importform=ImportForm())


@app.route('/<website>/', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
def website(website):
    return folder(website=website, folder='')


@app.route('/<website>/<folder>/_delete', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder')
    )
def folder_delete(website, folder):
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
    import_count = 0
    create_count = 0
    form = ImportForm()
    internal_imports = []
    if form.validate_on_submit():
        data = json.loads(request.files['import_file'].getvalue(), use_decimal=True)
        for inode in data['nodes']:
            mtime = parse_isoformat(inode.get('revision_updated_at', inode['updated_at']))
            node = Node.query.filter_by(folder=folder, uuid=inode['uuid']).first()
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
