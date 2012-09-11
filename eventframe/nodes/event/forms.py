# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from eventframe.forms import DateTimeField, DictField, timezone_list
from eventframe.nodes.content import ContentForm

__all__ = ['EventForm']


class EventForm(ContentForm):
    start_datetime = DateTimeField(u"Start date/time", validators=[wtf.Required()])
    end_datetime = DateTimeField(u"End date/time", validators=[wtf.Required()])
    timezone = wtf.SelectField(u"Timezone", choices=timezone_list, validators=[wtf.Required()])
    location_name = wtf.TextField(u"Location name", validators=[wtf.Required()])
    location_address = wtf.TextField(u"Address", validators=[wtf.Required()])
    map = wtf.QuerySelectField(u"Map", get_label='title', allow_blank=True)
    mapmarker = wtf.TextField(u"Map marker")
    capacity = wtf.IntegerField(u"Capacity", validators=[wtf.Required()])
    allow_waitlisting = wtf.BooleanField(u"Allow wait-listing if over capacity", default=False)
    allow_maybe = wtf.BooleanField(u"Allow “Maybe” responses", default=True)
    participant_list = wtf.QuerySelectField(u"Participant list", get_label='title', allow_blank=True)
    properties = DictField(u"Properties")
