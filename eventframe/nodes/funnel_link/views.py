# -*- coding: utf-8 -*-

from flask import request

from eventframe.nodes.content import ContentHandler
from eventframe.nodes.funnel_link.models import FunnelLink
from eventframe.nodes.funnel_link.forms import FunnelLinkForm

__all__ = ['FunnelLinkHandler', 'register']


class FunnelLinkHandler(ContentHandler):
    model = FunnelLink
    form_class = FunnelLinkForm
    title_new = "New funnel link"
    title_edit = "Edit funnel link"

    def make_form(self):
        form = super(FunnelLinkHandler, self).make_form()
        if request.method == 'GET':
            if self.node:
                form.funnel_name.data = self.node.funnel_name
            else:
                form.template.data = 'funnel.html.jinja2'
        return form

    def process_node(self):
        self.node.funnel_name = self.form.funnel_name.data


def register(registry):
    registry.register(FunnelLink, FunnelLinkHandler, render=True)
