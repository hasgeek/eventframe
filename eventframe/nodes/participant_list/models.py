# -*- coding: utf-8 -*-

from flask import url_for
from coaster import newsecret
from eventframe.nodes import User
from eventframe.nodes import db, BaseMixin, Node
from eventframe.nodes.content import ContentMixin

__all__ = ['Participant', 'ParticipantList']


# TODO: Implement import/export
class ParticipantList(ContentMixin, Node):
    __tablename__ = 'participant_list'

    source = db.Column(db.Unicode(80), nullable=False, default=u'')
    sourceid = db.Column(db.Unicode(80), nullable=False, default=u'')
    api_key = db.Column(db.Unicode(80), nullable=False, default=u'')
    participant_template = db.Column(db.Unicode(80), nullable=False, default=u'')

    def purge(self):
        """
        Discard all participants.
        """
        self.participants = []

    def has_user(self, user):
        return Participant.query.filter_by(participant_list=self).filter_by(user=user).first() is not None

    def url_for(self, action='view'):
        if action in ['sync', 'list']:
            return url_for('node_action',
                website=self.folder.website.name,
                folder=self.folder.name,
                node=self.name,
                action=action)
        else:
            return super(ParticipantList, self).url_for(action)


class Participant(BaseMixin, db.Model):
    __tablename__ = 'participant'

    #: List that this participant is in
    participant_list_id = db.Column(None, db.ForeignKey('participant_list.id'), nullable=False)
    #: Datetime when this participant's record was created upstream
    datetime = db.Column(db.DateTime, nullable=True)
    #: Ticket no, the reference key
    ticket = db.Column(db.Unicode(80), nullable=True, unique=True)
    #: Participant's name
    fullname = db.Column(db.Unicode(80), nullable=True)
    #: Unvalidated email address
    email = db.Column(db.Unicode(80), nullable=True)
    #: Unvalidated phone number
    phone = db.Column(db.Unicode(80), nullable=True)
    #: Unvalidated Twitter id
    twitter = db.Column(db.Unicode(80), nullable=True)
    #: Ticket type, if the registration system had multiple tickets
    ticket_type = db.Column(db.Unicode(80), nullable=True)
    #: Job title
    jobtitle = db.Column(db.Unicode(80), nullable=True)
    #: Company
    company = db.Column(db.Unicode(80), nullable=True)
    #: Participant's city
    city = db.Column(db.Unicode(80), nullable=True)
    #: T-shirt size
    tshirt_size = db.Column(db.Unicode(4), nullable=True)
    #: Link to the user record
    user_id = db.Column(None, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship(User)
    #: Access key for connecting to the user record (nulled when linked)
    access_key = db.Column(db.Unicode(44), nullable=True, default=newsecret, unique=True)
    #: Is listed in the public directory
    is_listed = db.Column(db.Boolean, default=False, nullable=False)
    #: Data fields the participant has chosen to reveal in public
    fields_directory = db.Column(db.Unicode(250), nullable=False,
        default=u'fullname company')
    #: Data fields the participant has chosen to reveal via ContactPoint
    fields_contactpoint = db.Column(db.Unicode(250), nullable=False,
        default=u'fullname email phone twitter jobtitle company city')

    participant_list = db.relationship(ParticipantList,
        backref=db.backref(
            'participants',
            order_by=fullname,
            cascade='all, delete-orphan'))

    parent = db.synonym('participant_list')
