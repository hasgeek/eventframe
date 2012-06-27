# -*- coding: utf-8 -*-

from flask import request, url_for, flash
from baseframe.forms import render_redirect
from eventframe.models import db, List
from eventframe.forms import ListForm
from eventframe.views import node_registry
from eventframe.views.content import AutoFormHandler


class ListHandler(AutoFormHandler):

    def make_form(self, folder, node):
        form = ListForm(obj=node)
        if node and request.method == 'GET':
            form.list.data = '\r\n'.join([unicode(item) for item in node._items])
        return form

    def process_form(self, folder, node, form):
        if node is None:
            node = List(folder=folder, name=form.name.data, title=form.title.data)
            flash(u"Created new list '%s'" % node.title, 'success')
        else:
            node.name = form.name.data
            node.title = form.title.data
            flash(u"Edited list '%s'" % node.title, 'success')
        node.populate_list([line.strip() for line in form.list.data.replace(
                '\r\n', '\n').replace('\r', '\n').split('\n')])
        db.session.commit()
        return render_redirect(url_for('folder', website=folder.website.name, folder=folder.name), code=303)

node_registry.register(List, ListHandler, render=False)
