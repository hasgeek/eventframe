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

    # Facilitate easier access to data

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data.keys())

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]
