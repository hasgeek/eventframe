# -*- coding: utf-8 -*-

from eventframe.nodes import Node
from eventframe.nodes.content import ContentMixin

__all__ = ['Post']


class Post(ContentMixin, Node):
    __tablename__ = 'post'
