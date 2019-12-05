# -*- coding: utf-8 -*-

from eventframe.nodes.content import ContentHandler
from eventframe.nodes.fragment.models import Fragment
from eventframe.nodes.fragment.forms import FragmentForm

__all__ = ['FragmentHandler', 'register']


class FragmentHandler(ContentHandler):
    model = Fragment
    form_class = FragmentForm
    title_new = "New page fragment"
    title_edit = "Edit page fragment"


def register(registry):
    registry.register(Fragment, FragmentHandler, render=False)
