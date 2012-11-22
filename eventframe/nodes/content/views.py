# -*- coding: utf-8 -*-

from flask import g, flash, url_for, request
from baseframe.forms import render_redirect
from eventframe.nodes import db, AutoFormHandler
from eventframe.nodes.content.forms import ContentForm

__all__ = ['ContentHandler']


class ContentHandler(AutoFormHandler):
    form_class = ContentForm

    def edit_tabs(self):
        if self.node:
            return [
                {'title': u"Edit", 'url': self.node.url_for('edit'), 'active': self.action == 'edit'},
                {'title': u"Publish", 'url': self.node.url_for('publish'), 'active': self.action == 'publish'},
                {'title': u"Unpublish", 'url': self.node.url_for('unpublish'), 'active': self.action == 'unpublish'},
                ]
        else:
            return []

    def make_form(self):
        # TODO: Add support for editing a specific revision
        if self.node:
            form = self.form_class(obj=self.node.last_revision())
            if request.method == 'GET':
                form.name.data = self.node.name
                form.properties.data = self.node.properties
                if hasattr(form, 'author'):
                    form.author.data = self.node.author
            return form
        else:
            return self.form_class()

    def process_node(self):
        if hasattr(self.form, 'author'):
            self.node.author = self.form.author.data

    def process_form(self):
        if self.node is None:
            # Creating a new object
            self.node = self.model(folder=self.folder, user=g.user)
            db.session.add(self.node)
        # Name isn't in revision history, so name changes
        # are applied to the node. TODO: Move this into a separate
        # rename action
        self.node.name = self.form.name.data
        # Make a revision and apply changes to it
        revision = self.node.revise()
        # FIXME: Not all form fields are in the revision object. Don't
        # use populate_obj here
        self.form.populate_obj(revision)
        self.node.properties = self.form.properties.data
        self.process_node()
        if not self.node.title:
            # New object. Copy title from first revision
            self.node.title = revision.title
        elif not self.node.is_published:
            # There is no published version, so use title from the draft
            self.node.title = revision.title
        if not self.node.id and not self.node.name:
            self.node.make_name()
        db.session.commit()
        # FIXME: Say created when created
        flash(u"Edited node '%s'." % self.node.title, 'success')
        return render_redirect(url_for('folder', website=self.website.name, folder=self.folder.name), code=303)
