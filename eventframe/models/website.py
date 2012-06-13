# -*- coding: utf-8 -*-

from datetime import datetime
from flask import Markup, g
from coaster import newid
from eventframe.models import db, BaseMixin, BaseNameMixin, BaseScopedNameMixin
from eventframe.models.user import User

__all__ = ['Website', 'Hostname', 'LoginCode', 'Folder', 'Page', 'PAGE_STATUS']


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

    def __init__(self, **kwargs):
        super(Website, self).__init__(**kwargs)
        root = Folder(name=u'', website=self)
        self.folders.append(root)
        root.pages[0].template = u'index.html'

    def __repr__(self):
        return u'<Website %s "%s">' % (self.name, self.title)


class Hostname(BaseMixin, db.Model):
    __tablename__ = 'hostname'
    #: Hostname that a website may be accessed at. Typically name:port
    name = db.Column(db.String(80), unique=True, nullable=False)
    #: Website this hostname applies to
    website_id = db.Column(db.Integer, db.ForeignKey('website.id'), nullable=False)
    website = db.relationship(Website,
        backref=db.backref('hostnames', cascade='all, delete-orphan'))

    def __repr__(self):
        return u'<Hostname %s>' % self.name


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


class Folder(BaseMixin, db.Model):
    __tablename__ = 'folder'
    #: Website this folder is under
    website_id = db.Column(db.Integer, db.ForeignKey('website.id'), nullable=False)
    website = db.relationship(Website,
        backref=db.backref('folders', cascade='all, delete-orphan'))

    # XXX: Do folders need titles? The per-folder blog feed needs a title
    #: Folder name (no title)
    name = db.Column(db.Unicode(80), nullable=False)
    _theme = db.Column("theme", db.Unicode(80), nullable=False, default=u'')

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
        index = Page(name=u'', title=u'Index', folder=self, template=u'page.html')
        index.name = u''  # Reset it to a blank
        self.pages.append(index)

    def __repr__(self):
        return u'<Folder %s at %s>' % (self.name or '(root)', self.website.name)


class PAGE_STATUS:
    DRAFT = 0
    PENDING = 1
    PUBLISHED = 2


class Page(BaseScopedNameMixin, db.Model):
    __tablename__ = 'page'
    #: User who made this page
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, default=default_user_id)
    user = db.relationship(User)

    #: Folder in which this page is located
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=False)
    folder = db.relationship(Folder,
        backref=db.backref('pages', cascade='all, delete-orphan'))
    parent = db.synonym('folder')

    #: Datetime at which this page becomes public. Eventframe will pretend the page
    #: doesn't exist until then. This field is also used to sort entries for blog
    #: feeds
    datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    #: Status of the page (draft, published)
    status = db.Column(db.Integer, default=0, nullable=False)

    #: Does this page show in the blog feed? Use for blog entries vs static pages
    blog = db.Column(db.Boolean, default=False, nullable=False)

    #: Is this page a fragment, meant to be embedded in a template?
    #: Fragment pages cannot be loaded by themselves
    fragment = db.Column(db.Boolean, default=False, nullable=False)

    #: Abstract that is shown in summaries. Plain text.
    description = db.Column(db.UnicodeText, nullable=False, default=u'')
    #: Page content. Rich text.
    _content = db.Column(db.UnicodeText, nullable=False, default=u'')

    #: Template with which this page will be rendered
    template = db.Column(db.Unicode(80), nullable=False, default=u'page.html')

    __table_args__ = (db.UniqueConstraint('name', 'folder_id'),)

    @property
    def content(self):
        return Markup(self._content)

    @content.setter
    def content(self, value):
        self._content = value

    content = db.synonym('_content', descriptor=content)

    def __repr__(self):
        return u'<Page %s/%s "%s" at %s>' % (self.folder.name, self.name or '(index)', self.title, self.folder.website.name)
