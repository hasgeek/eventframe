# -*- coding: utf-8 -*-

from pytz import utc, timezone
from flask import url_for
from coaster import parse_isoformat
from eventframe.models import db, BaseMixin, User
from eventframe.nodes import Node
from eventframe.nodes.content import ContentMixin
from eventframe.nodes.map import Map
from eventframe.nodes.participant_list import ParticipantList

__all__ = ['Event', 'EventAttendee']


# TODO: Implement import/export
class Event(ContentMixin, Node):
    __tablename__ = 'event'

    #: Start datetime for the event (in UTC)
    start_datetime = db.Column(db.DateTime, nullable=False)
    #: End datetime for the event (in UTC)
    end_datetime = db.Column(db.DateTime, nullable=False)
    #: Timezone as a string
    timezone = db.Column(db.Unicode(32), nullable=False)
    #: Location name
    location_name = db.Column(db.Unicode(80), nullable=False, default=u'')
    #: Location address
    location_address = db.Column(db.Unicode(250), nullable=False, default=u'')
    #: Location on map
    map_id = db.Column(None, db.ForeignKey('map.id'), nullable=True)
    map = db.relationship(Map, primaryjoin=map_id == Map.id)
    #: Map marker
    mapmarker = db.Column(db.Unicode(80), nullable=False, default=u'')
    #: Venue capacity, if attendance is capped
    capacity = db.Column(db.Integer, nullable=False, default=0)
    #: Allow wait-listing?
    allow_waitlisting = db.Column(db.Boolean, nullable=False, default=False)
    #: Allow a Maybe response?
    allow_maybe = db.Column(db.Boolean, nullable=False, default=True)
    #: Participant list to limit attendees to
    participant_list_id = db.Column(None, db.ForeignKey('participant_list.id'), nullable=True)
    participant_list = db.relationship(ParticipantList, primaryjoin=participant_list_id == ParticipantList.id)

    def _localize_time(self, value):
        return utc.localize(value).astimezone(timezone(self.timezone))

    @property
    def starts_at(self):
        return self._localize_time(self.start_datetime)

    @property
    def ends_at(self):
        return self._localize_time(self.end_datetime)

    def count(self):
        """Return count of confirmed attendees."""
        return len([a for a in self.attendees if a.status == u'Y'])

    def has_capacity(self):
        """Does the event have spare capacity for more attendees?"""
        if self.capacity == 0:
            return True
        else:
            return self.count() < self.capacity

    def can_rsvp(self, user):
        """Is this user authorized to participate?"""
        if self.participant_list:
            return self.participant_list.has_user(user)
        else:
            return True

    def set_status(self, user, status):
        """Set RSVP status for user."""
        if status not in [u'Y', u'N', u'M']:
            raise ValueError("Invalid status")
        if status == u'M' and not self.allow_maybe:
            raise ValueError(u"A “Maybe” response is not allowed")
        if not self.can_rsvp(user):
            raise ValueError("This user cannot participate")
        attendee = EventAttendee.query.filter_by(event=self, user=user).first()
        if not attendee:
            attendee = EventAttendee(event=self, user=user)
        if status == u'Y' and not self.has_capacity():
            if self.allow_waitlisting:
                status = u'W'
            else:
                raise ValueError("This event is over capacity")
        db.session.add(attendee)
        attendee.status = status

    def get_status(self, user):
        """Get RSVP status for this user."""
        attendee = EventAttendee.query.filter_by(event=self, user=user).first()
        if not attendee:
            return u'U'
        else:
            return attendee.status

    def url_for(self, action='view'):
        if action == 'rsvp':
            base = super(Event, self).url_for('view')
            if base.endswith('/'):
                return base + 'rsvp'
            else:
                return base + '/rsvp'
        elif action in ['list', 'csv', 'update', 'json']:
            return url_for('node_action',
                website=self.folder.website.name,
                folder=self.folder.name,
                node=self.name,
                action=action)
        else:
            return super(Event, self).url_for(action)

    def as_json(self):
        result = super(ContentMixin, self).as_json()
        result['start_datetime'] = self.start_datetime.isoformat() + 'Z'
        result['end_datetime'] = self.end_datetime.isoformat() + 'Z'
        result['timezone'] = self.timezone
        result['location_name'] = self.location_name
        result['location_address'] = self.location_address
        result['map'] = self.map.uuid if self.map else None
        result['mapmarker'] = self.mapmarker
        result['capacity'] = self.capacity
        result['allow_waitlisting'] = self.allow_waitlisting
        result['allow_maybe'] = self.allow_maybe
        result['participant_list'] = self.participant_list.uuid if self.participant_list else None
        return result

    def import_from(self, data):
        super(ContentMixin, self).import_from(data)
        self.start_datetime = parse_isoformat(data['start_datetime'])
        self.end_datetime = parse_isoformat(data['end_datetime'])
        self.timezone = data['timezone']
        self.location_name = data['location_name']
        self.location_address = data['location_address']
        self.mapmarker = data['mapmarker']
        self.capacity = data['capacity']
        self.allow_waitlisting = data['allow_waitlisting']
        self.allow_maybe = data['allow_maybe']

    def import_from_internal(self, data):
        super(ContentMixin, self).import_from_internal(data)
        if data.get('map'):
            self.map = Map.query.filter_by(uuid=data['map']).first()
        if data.get('participant_list'):
            self.participant_list = ParticipantList.query.filter_by(uuid=data['participant_list']).first()


class EventAttendee(BaseMixin, db.Model):
    __tablename__ = 'event_attendee'
    # User who is attending
    user_id = db.Column(None, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User)
    # Event that the user is attending
    event_id = db.Column(None, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship(Event, backref=db.backref('attendees', cascade='all, delete-orphan'))
    # Status codes: U/known, Y/es, N/o, M/aybe, W/ait-listed
    status = db.Column(db.Unicode(1), nullable=False, default=u'U')
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id'),)
