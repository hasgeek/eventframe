# -*- coding: utf-8 -*-

from flask import request, url_for, flash, json
from baseframe.forms import render_redirect
from eventframe.models import db, Map
from eventframe.forms import MapForm
from eventframe.views import node_registry
from eventframe.views.content import AutoFormHandler


class MapHandler(AutoFormHandler):

    def make_form(self):
        form = MapForm(obj=self.node)
        if self.node and request.method == 'GET':
            form.list.data = '\r\n'.join([json.dumps(row, use_decimal=True) for row in self.node.as_json()['items']])
        return form

    def process_form(self):
        if self.node is None:
            self.node = Map(folder=self.folder, name=self.form.name.data, title=self.form.title.data)
            db.session.add(self.node)
            flash(u"Created new list '%s'" % self.node.title, 'success')
        else:
            self.node.name = self.form.name.data
            self.node.title = self.form.title.data
            flash(u"Edited list '%s'" % self.node.title, 'success')
        self.node.populate_map([json.loads(row, use_decimal=True) for row in self.form.list.data.split('\n') if row.strip()])
        db.session.commit()
        return render_redirect(url_for('folder', website=self.website.name, folder=self.folder.name), code=303)

node_registry.register(Map, MapHandler, render=False)
