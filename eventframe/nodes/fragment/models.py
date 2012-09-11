# -*- coding: utf-8 -*-

from eventframe.nodes import Node
from eventframe.nodes.content import ContentMixin

__all__ = ['Fragment']


class Fragment(ContentMixin, Node):
    __tablename__ = 'fragment'
