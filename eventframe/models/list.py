# -*- coding: utf-8 -*-

from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy
from eventframe.models import db, BaseMixin
from eventframe.models.website import Folder, NodeMixin, Node


class ListItem(BaseMixin, db.Model):
    __tablename__ = 'list_item'
    list_id = db.Column(None, db.ForeignKey('list.id'), nullable=False)
    node_id = db.Column(None, db.ForeignKey('node.id'), nullable=False)
    node = db.relationship(Node, backref=db.backref('lists', cascade='all, delete-orphan'))
    seq = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint(list_id, node_id),)  # A node can only be in a list once

    @classmethod
    def get(cls, list, node):
        item = cls.query.filter_by(list=list, node=node).first()
        if item:
            return item
        else:
            item = cls(list=list, node=node)
            db.session.add(item)
        return item

    def __unicode__(self):
        return '%s/%s' % (self.node.folder.name, self.node.name)

    def __str__(self):
        return str(self.__unicode__())


class List(NodeMixin, Node):
    __tablename__ = 'list'
    _items = db.relationship(ListItem,
        order_by=[ListItem.seq],
        collection_class=ordering_list('seq'),
        backref='list',
        cascade='all, delete-orphan')

    def _new_node(self, node):
        return ListItem.get(self, node)

    items = association_proxy('_items', 'node', creator=_new_node)

    def as_json(self):
        result = super(NodeMixin, self).as_json()
        result['items'] = ['%s/%s' % (node.folder.name, node.name) for node in self.items]
        return result

    def populate_list(self, items):
        print "Populating with", items
        newitems = []
        for path in items:
            try:
                foldername, nodename = path.split('/', 1)
                if self.folder.name == foldername:
                    lfolder = self.folder
                else:
                    lfolder = Folder.query.filter_by(website=self.folder.website, name=foldername).first()
            except ValueError:
                # No folder specified? Try loading nodes from the current folder
                lfolder = self.folder
                nodename = path
            if not lfolder:
                # TODO: Log error and continue
                continue
            lnode = Node.query.filter_by(folder=lfolder, name=nodename).first()
            if lnode:
                litem = ListItem.get(self, lnode)
                newitems.append(litem)
                # TODO: If node not found, log error and continue

        self._items = newitems
        self._items.reorder()

    def import_from(self, data):
        super(NodeMixin, self).import_from(data)
        self.populate_list(data['items'])

    def prev_to(self, node, _items=None):
        items = _items or self.items

        candidate = None
        for i in items:
            if i is node:
                return candidate
            else:
                candidate = i
        # The given node is not in this list
        return None

    def next_to(self, node):
        # Reverse the list and search with prev_to
        return self.prev_to(node, _items=self.items[::-1])
