# -*- coding: utf-8 -*-

import wtforms
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from eventframe.forms import DateTimeField, DictField, timezone_list
from eventframe.nodes.content import ContentForm

__all__ = ['EventForm']


class EventForm(ContentForm):
    start_datetime = DateTimeField(u"Start date/time", validators=[wtforms.validators.Required()])
    end_datetime = DateTimeField(u"End date/time", validators=[wtforms.validators.Required()])
    timezone = wtforms.SelectField(u"Timezone", choices=timezone_list, validators=[wtforms.validators.Required()])
    location_name = wtforms.TextField(u"Location name", validators=[wtforms.validators.Required()])
    location_address = wtforms.TextField(u"Address", validators=[wtforms.validators.Required()])
    map = QuerySelectField(u"Map", get_label='title', allow_blank=True)
    mapmarker = wtforms.TextField(u"Map marker")
    capacity = wtforms.IntegerField(u"Capacity", validators=[wtforms.validators.Required()])
    allow_waitlisting = wtforms.BooleanField(u"Allow wait-listing if over capacity", default=False)
    allow_maybe = wtforms.BooleanField(u"Allow “Maybe” responses", default=True)
    participant_list = QuerySelectField(u"Participant list", get_label='title', allow_blank=True)
    properties = DictField(u"Properties")
