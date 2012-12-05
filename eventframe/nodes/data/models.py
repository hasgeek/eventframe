# -*- coding: utf-8 -*-

from coaster.sqlalchemy import JsonDict
from eventframe.nodes import db, NodeMixin, Node


class Data(NodeMixin, Node):
    __tablename__ = 'data'
    data = db.Column(JsonDict)

    def as_json(self):
        result = super(NodeMixin, self).as_json()
        result['data'] = self.data
        return result

    def import_from(self, data):
        super(NodeMixin, self).import_from(data)
        self.data = data['data']
