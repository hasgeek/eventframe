# -*- coding: utf-8 -*-

"""
Admin views
"""

from datetime import datetime
from coaster.views import load_model, load_models
from flask import g, flash, url_for, render_template, request, jsonify, json
from flask.ext.themes import get_themes_list
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqlamodel import ModelView
from baseframe.forms import render_form, render_redirect, render_delete_sqla

from eventframe import app, eventapp
from eventframe.models import db, User, Website, Folder, Page
from eventframe.forms import WebsiteForm, HostnameForm, FolderForm, PageForm, ImportForm
from eventframe.views.login import lastuser

admin = Admin(name='Eventframe')


@app.route('/_new', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
def website_new():
    form = WebsiteForm()
    with eventapp.test_request_context():
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
    with eventapp.test_request_context():
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
        next=url_for('index'), ajax=True)


@app.route('/<website>/_new', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Website, {'name': 'website'}, 'website')
def folder_new(website):
    form = FolderForm()
    with eventapp.test_request_context():
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
    with eventapp.test_request_context():
        themes = [('', 'Website Default')] + [(t.identifier, t.name) for t in get_themes_list()]
    form.theme.choices = themes
    if form.validate_on_submit():
        form.populate_obj(folder)
        db.session.commit()
        return render_redirect(url_for('folder', website=website.name, folder=folder.name), code=303)
    return render_form(form=form, title=u"Edit folder", submit=u"Create",
        cancel_url=url_for('folder', website=website.name, folder=folder.name), ajax=True)


@app.route('/<website>/<folder>', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder')
    )
def folder(website, folder):
    return render_template('folder.html', website=website, folder=folder)


@app.route('/<website>/', methods=['GET', 'POST'])
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
    return jsonify(
        website=website.name,
        folder=folder.name,
        pages=[{
          'name': page.name,
          'title': page.title,
          'created_at': page.created_at.isoformat() + 'Z',
          'updated_at': page.updated_at.isoformat() + 'Z',
          'userid': page.user.userid,
          'redirect_url': page.redirect_url,
          'datetime': page.datetime.isoformat() + 'Z',
          'status': page.status,
          'blog': page.blog,
          'fragment': page.fragment,
          'description': page.description,
          'content': page.content,
          'template': page.template,
        } for page in folder.pages])


def parse_isoformat(text):
    try:
        return datetime.strptime(text, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        return datetime.strptime(text, '%Y-%m-%dT%H:%M:%SZ')


@app.route('/<website>/<folder>/_import', methods=['GET', 'POST'])
@app.route('/<website>/_root/_import', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder')
    )
def folder_import(website, folder):
    form = ImportForm()
    if form.validate_on_submit():
        data = json.loads(request.files['file'].getvalue())
        for ipage in data['pages']:
            mtime = parse_isoformat(ipage['updated_at'])
            page = Page.query.filter_by(folder=folder, name=ipage['name']).first()
            if page is None:
                page = Page(folder=folder)
                db.session.add(page)
            else:
                if form.import_updated.data and mtime < page.updated_at:
                    continue
            page.name = ipage['name']
            page.title = ipage['title']
            page.redirect_url = ipage['redirect_url']
            page.datetime = parse_isoformat(ipage['datetime'])
            page.status = ipage['status']
            page.blog = ipage['blog']
            page.fragment = ipage['fragment']
            page.description = ipage['description']
            page.content = ipage['content']
            page.template = ipage['template']
            if form.preserve_user.data:
                user = User.query.filter_by(userid=ipage['userid']).first()
                if not user:
                    # Keep page's existing user unless it's a new page
                    user = page.user or g.user
            else:
                user = g.user
            page.user = user
        db.session.commit()
        flash("Pages imported", "success")
        return render_redirect(url_for('folder', website=website.name, folder=folder.name), code=303)
    return render_form(form=form, title=u"Import pages", submit=u"Upload",
        cancel_url=url_for('folder', website=website.name, folder=folder.name))


@app.route('/<website>/<folder>/_new', methods=['GET', 'POST'])
@app.route('/<website>/_root/_new', defaults={'folder': u''}, methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder')
    )
def page_new(website, folder):
    form = PageForm()
    form.datetime.data = datetime.utcnow()
    if form.validate_on_submit():
        page = Page(folder=folder, user=g.user)
        form.populate_obj(page)
        if not page.name:
            page.make_name()
        if page.redirect_url:
            page.fragment = True
        else:
            page.redirect_url = None
        db.session.add(page)
        db.session.commit()
        flash("Created page '%s'." % page.title, 'success')
        return render_redirect(url_for('folder', website=website.name, folder=folder.name), code=303)
    return render_form(form=form, title=u"New page", submit=u"Save",
        cancel_url=url_for('folder', website=website.name, folder=folder.name))


@app.route('/<website>/<folder>/<page>/_edit', methods=['GET', 'POST'])
@app.route('/<website>/_root/<page>/_edit', defaults={'folder': u''}, methods=['GET', 'POST'])
@app.route('/<website>/<folder>/_index/_edit', defaults={'page': u''}, methods=['GET', 'POST'])
@app.route('/<website>/_root/_index/_edit', defaults={'folder': u'', 'page': u''}, methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder'),
    (Page, {'name': 'page', 'folder': 'folder'}, 'page')
    )
def page_edit(website, folder, page):
    form = PageForm(obj=page)
    if form.validate_on_submit():
        form.populate_obj(page)
        if page.redirect_url:
            page.fragment = True
        else:
            page.redirect_url = None
        db.session.commit()
        flash("Edited page '%s'." % page.title, 'success')
        return render_redirect(url_for('folder', website=website.name, folder=folder.name), code=303)
    return render_form(form=form, title=u"Edit page", submit=u"Save",
        cancel_url=url_for('folder', website=website.name, folder=folder.name))


@app.route('/<website>/<folder>/<page>/_delete', methods=['GET', 'POST'])
@app.route('/<website>/_root/<page>/_delete', defaults={'folder': u''}, methods=['GET', 'POST'])
@app.route('/<website>/<folder>/_index/_delete', defaults={'page': u''}, methods=['GET', 'POST'])
@app.route('/<website>/_root/_index/_delete', defaults={'folder': u'', 'page': u''}, methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder'),
    (Page, {'name': 'page', 'folder': 'folder'}, 'page')
    )
def page_delete(website, folder, page):
    return render_delete_sqla(page, db, title=u"Confirm delete",
        message=u"Delete page '%s'? This is permanent. There is no undo." % website.title,
        success=u"You have deleted page '%s'." % page.title,
        next=url_for('folder', website=website.name, folder=folder.name))


class AuthModelView(ModelView):
    def is_accessible(self):
        return lastuser.has_permission('siteadmin')


def init_model_views():
    from eventframe.models import db, User, Website, Folder, Page
    admin.add_view(AuthModelView(User, db.session))
    admin.add_view(AuthModelView(Website, db.session))
    admin.add_view(AuthModelView(Folder, db.session))
    admin.add_view(AuthModelView(Page, db.session))
