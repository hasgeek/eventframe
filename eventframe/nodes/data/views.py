# -*- coding: utf-8 -*-

from flask import request, url_for, flash
import simplejson as json
from baseframe.forms import render_redirect
from eventframe.nodes import db, AutoFormHandler
from eventframe.nodes.data.models import Data
from eventframe.nodes.data.forms import DataForm

__all__ = ['DataHandler', 'register']


class DataHandler(AutoFormHandler):

    def make_form(self):
        form = DataForm(obj=self.node)
        if self.node and request.method == 'GET':
            form.data.data = json.dumps(self.node.data)
        return form

    def process_form(self):
        if self.node is None:
            self.node = Data(folder=self.folder, name=self.form.name.data, title=self.form.title.data)
            db.session.add(self.node)
            flash(u"Created new data node '%s'" % self.node.title, 'success')
        else:
            self.node.name = self.form.name.data
            self.node.title = self.form.title.data
            flash(u"Edited data node '%s'" % self.node.title, 'success')
        self.node.data = json.loads(self.form.data.data, use_decimal=True)
        db.session.commit()
        return render_redirect(url_for('folder', website=self.website.name, folder=self.folder.name), code=303)


def register(registry):
    registry.register(Data, DataHandler, render=False)
