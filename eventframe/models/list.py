# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.ext.orderinglist import ordering_list
from eventframe.models import db, BaseMixin
from eventframe.models.website import Folder, NodeMixin, Node


class ListItem(BaseMixin, db.Model):
    __tablename__ = 'list_item'
    list_id = db.Column(None, db.ForeignKey('list.id'), nullable=False)
    name = db.Column(db.Unicode(80), nullable=True)
    title = db.Column(db.Unicode(250), nullable=True)
    url = db.Column(db.Unicode(250), nullable=True)
    node_id = db.Column(None, db.ForeignKey('node.id'), nullable=True)
    node = db.relationship(Node, backref=db.backref('lists', cascade='all, delete-orphan'))
    seq = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('list_id', 'name'),    # name, if present, must be unique in this list
        db.UniqueConstraint('list_id', 'node_id')  # A node can only be in a list once
        )

    @classmethod
    def get_or_new(cls, list, name=None, node=None):
        if name is None and node is None:
            return
        query = cls.query.filter_by(list=list)
        if name:
            query = query.filter_by(name=name)
        if node:
            query = query.filter_by(node=node)
        item = query.first()
        if item:
            return item
        else:
            item = cls(list=list, name=name, node=node)
            db.session.add(item)
        return item


class List(NodeMixin, Node):
    __tablename__ = 'list'
    items = db.relationship(ListItem,
        order_by=[ListItem.seq],
        collection_class=ordering_list('seq'),
        backref='list',
        cascade='all, delete-orphan')

    def as_json(self):
        result = super(NodeMixin, self).as_json()
        result['items'] = [[item.name,
                            item.title,
                            item.url,
                            '%s/%s' % (item.node.folder.name, item.node.name) if item.node else '']
            for item in self.items]
        return result

    def populate_list(self, items):
        newitems = []
        for name, title, url, path in items:
            name = name or None  # Convert blank strings into None
            litem = None
            if path:
                try:
                    foldername, nodename = path.split('/', 1)
                except ValueError:
                    # No folder specified? Try loading nodes from the current folder
                    lfolder = self.folder
                    nodename = path
                else:
                    if self.folder.name == foldername:
                        lfolder = self.folder
                    else:
                        lfolder = Folder.query.filter_by(website=self.folder.website, name=foldername).first()

                if lfolder:
                    lnode = Node.query.filter_by(folder=lfolder, name=nodename).first()
                    if lnode:
                        litem = ListItem.get_or_new(self, node=lnode)
                        # If this item has a name, ensure the name is unique
                        if name is not None:
                            for existing in self.items:
                                if existing is not litem and existing.name == name:
                                    existing.name = None
                        litem.name = name
                        litem.title = title
                        litem.url = url
            if name and litem is None:
                litem = ListItem.get_or_new(self, name=name)
                litem.title = title
                litem.url = url
                litem.node = None
            if litem is None:
                litem = ListItem(name=name, title=title, node=None, url=url)
            newitems.append(litem)

        self.items = newitems
        self.items.reorder()
        # Since self.items is a relationship, it won't update self.updated_at
        self.updated_at = datetime.utcnow()

    def import_from(self, data):
        super(NodeMixin, self).import_from(data)

    def import_from_internal(self, data):
        super(NodeMixin, self).import_from_internal(data)
        self.populate_list(data['items'])

    def get_by_node(self, node):
        if node is not None:
            for i in self.items:
                if i.node == node:
                    return i

    def prev_to(self, item, items=None):
        items = items or self.items

        candidate = None
        for i in items:
            if i == item:
                return candidate
            else:
                candidate = i
        # The given node is not in this list
        return None

    def next_to(self, item):
        # Reverse the list and search with prev_to
        return self.prev_to(item, items=self.items[::-1])

    def prev_to_node(self, node, items=None):
        items = items or self.items

        candidate = None
        for i in items:
            if i.node == node:
                return candidate
            else:
                candidate = i
        # The given node is not in this list
        return None

    def next_to_node(self, node):
        # Reverse the list and search with prev_to
        return self.prev_to_node(node, items=self.items[::-1])
