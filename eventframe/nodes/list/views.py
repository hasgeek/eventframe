# -*- coding: utf-8 -*-

from flask import request, url_for, flash
import simplejson as json
from baseframe.forms import render_redirect
from eventframe.nodes import db, AutoFormHandler
from eventframe.nodes.list.models import List
from eventframe.nodes.list.forms import ListForm

__all__ = ['ListHandler', 'register']


class ListHandler(AutoFormHandler):

    def make_form(self):
        form = ListForm(obj=self.node)
        if self.node and request.method == 'GET':
            form.list.data = '\r\n'.join([json.dumps(row, use_decimal=True) for row in self.node.as_json()['items']])
        return form

    def process_form(self):
        if self.node is None:
            self.node = List(folder=self.folder, name=self.form.name.data, title=self.form.title.data)
            db.session.add(self.node)
            flash("Created new list '%s'" % self.node.title, 'success')
        else:
            self.node.name = self.form.name.data
            self.node.title = self.form.title.data
            flash("Edited list '%s'" % self.node.title, 'success')
        self.node.populate_list([json.loads(row, use_decimal=True) for row in self.form.list.data.split('\n') if row.strip()])
        db.session.commit()
        return render_redirect(url_for('folder', website=self.website.name, folder=self.folder.name), code=303)


def register(registry):
    registry.register(List, ListHandler, render=False)
