# -*- coding: utf-8 -*-

import wtforms
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from eventframe.forms import DateTimeField, DictField, timezone_list
from eventframe.nodes.content import ContentForm

__all__ = ['EventForm']


class EventForm(ContentForm):
    start_datetime = DateTimeField("Start date/time", validators=[wtforms.validators.Required()])
    end_datetime = DateTimeField("End date/time", validators=[wtforms.validators.Required()])
    timezone = wtforms.SelectField("Timezone", choices=timezone_list, validators=[wtforms.validators.Required()])
    location_name = wtforms.TextField("Location name", validators=[wtforms.validators.Required()])
    location_address = wtforms.TextField("Address", validators=[wtforms.validators.Required()])
    map = QuerySelectField("Map", get_label='title', allow_blank=True)
    mapmarker = wtforms.TextField("Map marker")
    capacity = wtforms.IntegerField("Capacity", validators=[wtforms.validators.Required()])
    allow_waitlisting = wtforms.BooleanField("Allow wait-listing if over capacity", default=False)
    allow_maybe = wtforms.BooleanField("Allow “Maybe” responses", default=True)
    participant_list = QuerySelectField("Participant list", get_label='title', allow_blank=True)
    properties = DictField("Properties")
