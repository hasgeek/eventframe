# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.ext.orderinglist import ordering_list
from eventframe.models import db, BaseScopedNameMixin
from eventframe.models.website import NodeMixin, Node


class MapItem(BaseScopedNameMixin, db.Model):
    __tablename__ = 'map_item'
    map_id = db.Column(None, db.ForeignKey('map.id'), nullable=False)
    parent = db.synonym('map')
    url = db.Column(db.Unicode(250), nullable=True)
    latitude = db.Column(db.Numeric(7, 4), nullable=False)
    longitude = db.Column(db.Numeric(7, 4), nullable=False)
    zoomlevel = db.Column(db.Integer, nullable=True)
    marker = db.Column(db.Unicode(80), nullable=True)
    seq = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint('map_id', 'name'),)

    @classmethod
    def get_or_new(cls, map, name=None):
        item = cls.query.filter_by(map=map, name=name).first()
        if item is None:
            item = cls(map=map, name=name)
            db.session.add(item)
        return item


class Map(NodeMixin, Node):
    __tablename__ = 'map'
    items = db.relationship(MapItem,
        order_by=[MapItem.seq],
        collection_class=ordering_list('seq'),
        backref='map',
        cascade='all, delete-orphan')

    def as_json(self):
        result = super(NodeMixin, self).as_json()
        result['items'] = [{'name': item.name,
                            'title': item.title,
                            'url': item.url,
                            'latitude': item.latitude,
                            'longitude': item.longitude,
                            'zoomlevel': item.zoomlevel,
                            'marker': item.marker}
            for item in self.items]
        return result

    def populate_map(self, items):
        newitems = []
        for itemdata in items:
            mitem = MapItem.get_or_new(self, name=itemdata['name'])
            for key in itemdata:
                setattr(mitem, key, itemdata[key])
            newitems.append(mitem)

        self.items = newitems
        self.items.reorder()
        # Since self.items is a relationship, it won't update self.updated_at
        self.updated_at = datetime.utcnow()

    def import_from(self, data):
        super(NodeMixin, self).import_from(data)
        self.populate_map(data['items'])

    def prev_to(self, item, items=None):
        items = items or self.items

        candidate = None
        for i in items:
            if i is item:
                return candidate
            else:
                candidate = i
        # The given item is not in this list
        return None

    def next_to(self, item):
        # Reverse the list and search with prev_to
        return self.prev_to(item, items=self.items[::-1])
