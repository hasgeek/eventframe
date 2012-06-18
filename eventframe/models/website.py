# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from flask import g
from coaster import newid, parse_isoformat
from eventframe.models import db, TimestampMixin, BaseMixin, BaseNameMixin, BaseScopedNameMixin
from eventframe.models.user import User

__all__ = ['Website', 'Hostname', 'LoginCode', 'Folder', 'Node', 'NodeMixin']


def default_user_id():
    return g.user.id if g.user else None


class Website(BaseNameMixin, db.Model):
    __tablename__ = 'website'
    #: URL to the website
    url = db.Column(db.Unicode(80), nullable=False, default=u'')
    #: Theme that this website uses as the default (folders can override)
    theme = db.Column(db.Unicode(80), nullable=False, default=u'default')
    #: Typekit code, if used
    typekit_code = db.Column(db.Unicode(20), nullable=False, default=u'')
    #: Google Analytics code, if used
    googleanalytics_code = db.Column(db.Unicode(20), nullable=False, default=u'')

    _hostnames = db.relationship("Hostname", cascade='all, delete-orphan', backref='website')
    hostnames = association_proxy('_hostnames', 'name',
        creator=lambda name: Hostname.get(name=name))

    def __init__(self, **kwargs):
        super(Website, self).__init__(**kwargs)
        root = Folder(name=u'', title=u'', website=self)
        self.folders.append(root)
        #root.pages[0].template = u'index.html'

    def __repr__(self):
        return u'<Website %s "%s">' % (self.name, self.title)


class Hostname(BaseMixin, db.Model):
    __tablename__ = 'hostname'
    #: Hostname that a website may be accessed at. Typically name:port
    name = db.Column(db.String(80), unique=True, nullable=False)
    #: Website this hostname applies to
    website_id = db.Column(db.Integer, db.ForeignKey('website.id'), nullable=False)

    def __repr__(self):
        return u'<Hostname %s>' % self.name

    @classmethod
    def get(cls, name, website=None):
        hostname = cls.query.filter_by(name=name).first()
        return hostname or cls(name=name, website=website)


class LoginCode(BaseMixin, db.Model):
    __tablename__ = 'logincode'
    #: Tracking code to enable users to login to an event website
    code = db.Column(db.Unicode(22), nullable=False, unique=True)
    #: User who logged in
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=None)
    user = db.relationship(User)
    #: URL on event website to return user to
    next_url = db.Column(db.Unicode(250), nullable=False)
    #: Login handler URL on event website
    return_url = db.Column(db.Unicode(250), nullable=False)

    def __init__(self, **kwargs):
        super(LoginCode, self).__init__(**kwargs)
        self.code = newid()


class Folder(BaseScopedNameMixin, db.Model):
    __tablename__ = 'folder'
    #: Website this folder is under
    website_id = db.Column(db.Integer, db.ForeignKey('website.id'), nullable=False)

    _theme = db.Column("theme", db.Unicode(80), nullable=False, default=u'')

    website = db.relationship(Website,
        backref=db.backref('folders', order_by='Folder.name', cascade='all, delete-orphan'))
    parent = db.synonym('website')
    __table_args__ = (db.UniqueConstraint('name', 'website_id'),)

    @property
    def theme(self):
        return self._theme or self.website.theme

    @theme.setter
    def theme(self, value):
        self._theme = value

    #: Theme used by the folder. Defaults to the website's theme.
    theme = db.synonym('_theme', descriptor=theme)

    def __init__(self, **kwargs):
        super(Folder, self).__init__(**kwargs)
        #index = Page(name=u'', title=u'Index', folder=self, template=u'page.html')
        #index.name = u''  # Reset it to a blank
        #self.pages.append(index)

    def __repr__(self):
        return u'<Folder %s at %s>' % (self.name or '(root)', self.website.name)


class Node(BaseScopedNameMixin, db.Model):
    __tablename__ = 'node'
    #: Id of the node across sites (staging, production, etc) for import/export
    uuid = db.Column(db.Unicode(22), unique=True, default=newid, nullable=False)
    #: User who made this node
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, default=default_user_id)
    user = db.relationship(User)
    #: Folder in which this node is located
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=False)
    folder = db.relationship(Folder,
        backref=db.backref('nodes', order_by='Node.name', cascade='all, delete-orphan'))
    parent = db.synonym('folder')
    #: Publication date
    published_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    #: Type of node, for polymorphic identity
    type = db.Column('type', db.Unicode(20))
    __table_args__ = (db.UniqueConstraint('name', 'folder_id'),)
    __mapper_args__ = {'polymorphic_on': type}

    def as_json(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'title': self.title,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
            'published_at': self.published_at.isoformat() + 'Z',
            'userid': self.user.userid,
            'type': self.type,
        }

    def import_from(self, data):
        self.name = data['name']
        self.title = data['title']
        self.published_at = parse_isoformat(data['published_at'])


class NodeMixin(TimestampMixin):
    @declared_attr
    def id(cls):
        """Link back to node"""
        return db.Column(db.Integer, db.ForeignKey('node.id'), primary_key=True, nullable=False)

    @declared_attr
    def __mapper_args__(cls):
        """Use the table name as the polymorphic identifier"""
        return {'polymorphic_identity': cls.__tablename__}
