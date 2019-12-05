# -*- coding: utf-8 -*-

from eventframe.nodes.content import ContentHandler
from eventframe.nodes.page.models import Page

__all__ = ['PageHandler', 'register']


class PageHandler(ContentHandler):
    model = Page
    title_new = "New page"
    title_edit = "Edit page"


def register(registry):
    registry.register(Page, PageHandler, render=True)
