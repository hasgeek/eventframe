# -*- coding: utf-8 -*-

from datetime import datetime
from flask import Markup, url_for
from sqlalchemy.ext.declarative import declared_attr
from coaster.utils import parse_isoformat
from eventframe.nodes import db, BaseMixin, User, default_user_id, NodeMixin

__all__ = ['ContentMixin']


class ContentRevision(BaseMixin, db.Model):
    """
    A single revision of any piece of content.
    """
    __tablename__ = 'content_revision'
    parent_id = db.Column(db.Integer, db.ForeignKey('revisions.id', use_alter=True,
        name='content_revision_parent_id_fkey'), nullable=False)
    #: Previous revision
    previous_id = db.Column(db.Integer, db.ForeignKey('content_revision.id'), nullable=True)
    previous = db.relationship('ContentRevision', remote_side='ContentRevision.id', uselist=False)
    #: User who made this content revision
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, default=default_user_id)
    user = db.relationship(User)
    #: Title of the current revision
    title = db.Column(db.Unicode(250), nullable=False)
    #: Abstract that is shown in summaries. Plain text.
    description = db.Column(db.UnicodeText, nullable=False, default=u'')
    #: Page content. Rich text.
    _content = db.Column('content', db.UnicodeText, nullable=False, default=u'')
    #: Template with which this page will be rendered
    template = db.Column(db.Unicode(80), nullable=False, default=u'')

    def __init__(self, **kwargs):
        super(ContentRevision, self).__init__(**kwargs)
        if self.previous:
            # Copy over content from the previous revision
            if not self.user:
                self.user = self.previous.user
            if not self.title:
                self.title = self.previous.title
            if not self.description:
                self.description = self.previous.description
            if not self._content:
                self._content = self.previous._content
            if not self.template:
                self.template = self.previous.template

    @property
    def content(self):
        return Markup(self._content)

    @content.setter
    def content(self, value):
        self._content = value

    content = db.synonym('_content', descriptor=content)


class Revisions(BaseMixin, db.Model):
    """
    Collection of revisions of content.
    """
    __tablename__ = 'revisions'
    #: All revisions of the content
    history = db.relationship(ContentRevision, primaryjoin='ContentRevision.parent_id == Revisions.id',
        order_by=ContentRevision.id.desc,
        backref=db.backref('parent', cascade='all'))
    #: Latest published revision
    published_id = db.Column(db.Integer, db.ForeignKey('content_revision.id'), nullable=True)
    published = db.relationship(ContentRevision, post_update=True,
        primaryjoin=published_id == ContentRevision.id)
    #: Latest draft revision
    draft_id = db.Column(db.Integer, db.ForeignKey('content_revision.id'), nullable=True)
    draft = db.relationship(ContentRevision, post_update=True,
        primaryjoin=draft_id == ContentRevision.id)


class ContentMixin(NodeMixin):
    is_published = db.Column('published', db.Boolean, default=False, nullable=False, index=True)

    @declared_attr
    def revisions_id(cls):
        return db.Column(db.Integer, db.ForeignKey('revisions.id'), nullable=False)

    @declared_attr
    def revisions(cls):
        return db.relationship(Revisions, uselist=False)

    def __init__(self, **kwargs):
        self.revisions = Revisions()
        super(ContentMixin, self).__init__(**kwargs)

    def last_revision(self):
        revision = self.revisions.draft or self.revisions.published
        if revision is None:
            with db.session.no_autoflush:
                revision = ContentRevision.query.filter_by(parent=self.revisions).order_by(db.desc('id')).limit(1).first()
        return revision

    def publish(self, revision=None):
        """
        Publish the given revision, or the latest draft.
        """
        if revision is not None and revision.parent is not self.revisions:
            raise ValueError("This revision isn't from this content document.")
        if revision is None:
            revision = self.revisions.draft
        if revision is not None:
            if not self.revisions.published:
                # TODO: Expose this for user editing. Don't assume current
                self.published_at = datetime.utcnow()
            self.revisions.published = revision
            self.is_published = True
            # Update node title from the revision
            self.title = revision.title
            # If this was the latest draft, there's no longer a latest draft
            if revision is self.revisions.draft:
                self.revisions.draft = None

    def unpublish(self):
        """
        Withdraw the published version and go back to being a draft.
        """
        self.revisions.published = None
        revision = ContentRevision.query.filter_by(parent=self.revisions).order_by(db.desc('id')).limit(1).first()
        self.revisions.draft = revision
        self.title = revision.title
        self.is_published = False

    def revise(self, revision=None):
        """Create and return a new revision."""
        if revision and revision.parent is not self.revisions:
            raise ValueError("This revision isn't from this content document.")
        # Make and return a new revision based on the given revision or the latest draft
        if revision is None:
            # If parent is still None after this, there was no parent
            revision = self.last_revision()
        with db.session.no_autoflush:
            new_revision = ContentRevision(parent=self.revisions, previous=revision)
            self.revisions.draft = new_revision
            db.session.add(new_revision)
        return new_revision

    @property
    def template(self):
        if self.revisions.published:
            return self.revisions.published.template
        else:
            return self.revisions.draft.template

    @property
    def description(self):
        # TODO: Only show drafts to a logged in, authorized user
        if self.is_published:
            return self.revisions.published.description
        else:
            return self.revisions.draft.description

    @property
    def content(self):
        # TODO: Only show drafts to a logged in, authorized user
        if self.is_published:
            return self.revisions.published.content
        else:
            return self.revisions.draft.content

    def __repr__(self):
        return u'<%s %s/%s "%s" at %s>' % (self.__tablename__.title(), self.folder.name, self.name or '(index)',
            self.title, self.folder.website.name)

    def as_json(self):
        result = super(ContentMixin, self).as_json()
        revision = self.revisions.draft or self.revisions.published
        if not revision:
            return result

        result.update({
            'title': revision.title,
            'description': revision.description,
            'content': revision.content,
            'template': revision.template,
            'revision_created_at': revision.created_at.isoformat() + 'Z',
            'revision_updated_at': revision.updated_at.isoformat() + 'Z',
            'is_published': self.is_published,
            })
        return result

    def import_from(self, data):
        super(ContentMixin, self).import_from(data)
        last = self.last_revision()
        if last and last.updated_at >= parse_isoformat(data['revision_updated_at']):
            # Don't import if data is older than or the same as the last revision
            return
        revision = self.revise()
        revision.title = data['title']
        revision.description = data['description']
        revision.content = data['content']
        revision.template = data['template']

    def url_for(self, action='view', _external=False):
        if action == 'publish':
            return url_for('node_publish',
                website=self.folder.website.name,
                folder=self.folder.name,
                node=self.name,
                _external=_external)
        elif action == 'unpublish':
            return url_for('node_unpublish',
                website=self.folder.website.name,
                folder=self.folder.name,
                node=self.name,
                _external=_external)
        else:
            return super(ContentMixin, self).url_for(action, _external=_external)
