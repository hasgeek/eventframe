# -*- coding: utf-8 -*-

from eventframe.nodes import db, Node, NodeMixin

__all__ = ['Redirect']


class Redirect(NodeMixin, Node):
    __tablename__ = 'redirect'
    redirect_url = db.Column(db.Unicode(250), nullable=False)

    def as_json(self):
        result = super(Redirect, self).as_json()
        result.update({'redirect_url': self.redirect_url})
        return result

    def import_from(self, data):
        super(Redirect, self).import_from(data)
        self.redirect_url = data['redirect_url']
