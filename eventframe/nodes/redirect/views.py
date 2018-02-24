# -*- coding: utf-8 -*-

from flask import flash, url_for, redirect
from coaster.auth import current_auth
from baseframe.forms import render_redirect

from eventframe.nodes import db, AutoFormHandler, NodeHandler
from eventframe.nodes.redirect.models import Redirect
from eventframe.nodes.redirect.forms import RedirectForm

__all__ = ['RedirectHandler', 'RedirectViewHandler', 'register']


class RedirectHandler(AutoFormHandler):
    model = Redirect
    title_new = u"New redirect"
    title_edit = u"Edit redirect"

    def make_form(self):
        return RedirectForm(obj=self.node)

    def process_form(self):
        if self.node is None:
            self.node = self.model(folder=self.folder, user=current_auth.user)
            db.session.add(self.node)
        self.form.populate_obj(self.node)
        db.session.commit()
        flash(u"Edited redirect '%s'." % self.node.title, 'success')
        return render_redirect(url_for('folder', website=self.website.name, folder=self.folder.name), code=303)


class RedirectViewHandler(NodeHandler):
    def GET(self):
        return redirect(self.node.redirect_url)


def register(registry):
    registry.register(Redirect, RedirectHandler, view_handler=RedirectViewHandler, render=False)
