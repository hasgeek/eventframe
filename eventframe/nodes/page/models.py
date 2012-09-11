# -*- coding: utf-8 -*-

from eventframe.nodes import Node
from eventframe.nodes.content import ContentMixin

__all__ = ['Page']


class Page(ContentMixin, Node):
    __tablename__ = 'page'
