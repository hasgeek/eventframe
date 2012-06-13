# -*- coding: utf-8 -*-

"""
Admin views
"""

from coaster.views import load_models
from flask import flash, url_for
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqlamodel import ModelView
from baseframe.forms import render_form, render_redirect

from eventframe import app
from eventframe.models import db, Website, Folder, Page
from eventframe.forms import PageForm
from eventframe.views.login import lastuser

admin = Admin(name='Eventframe')


@app.route('/<website>/<folder>/<page>/edit', methods=['GET', 'POST'])
@app.route('/<website>/_root/<page>/edit', defaults={'folder': u''}, methods=['GET', 'POST'])
@app.route('/<website>/<folder>/_index/edit', defaults={'page': u''}, methods=['GET', 'POST'])
@app.route('/<website>/_root/_index/edit', defaults={'folder': u'', 'page': u''}, methods=['GET', 'POST'])
@load_models(
    (Website, {'name': 'website'}, 'website'),
    (Folder, {'name': 'folder', 'website': 'website'}, 'folder'),
    (Page, {'name': 'page', 'folder': 'folder'}, 'page')
    )
def page_edit(website, folder, page):
    form = PageForm(obj=page)
    if form.validate_on_submit():
        form.populate_obj(page)
        db.session.commit()
        flash("Edited page '%s'." % page.title, 'success')
        return render_redirect(url_for('index'), code=303)
    return render_form(form=form, title=u"Edit page", submit=u"Save", cancel_url=url_for('index'))


class AuthModelView(ModelView):
    def is_accessible(self):
        return lastuser.has_permission('siteadmin')


def init_model_views():
    from eventframe.models import db, User, Website, Folder, Page
    admin.add_view(AuthModelView(User, db.session))
    admin.add_view(AuthModelView(Website, db.session))
    admin.add_view(AuthModelView(Folder, db.session))
    admin.add_view(AuthModelView(Page, db.session))
