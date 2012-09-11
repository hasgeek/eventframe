# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from eventframe.forms import DictField
from eventframe.nodes.content import ContentForm

__all__ = ['ParticipantListForm']


class ParticipantListForm(ContentForm):
    source = wtf.SelectField(u"Data Source", choices=[
        ('', ''), ('doattend', 'DoAttend')],
        description=u"Source from which the participant list will be retrieved.")
    sourceid = wtf.TextField(u"Event id",
        description=u"Id of this event at the selected data source.")
    api_key = wtf.TextField(u"API Key",
        description=u"API key to retrieve data from the selected data source.")
    participant_template = wtf.TextField("Participant template",
        validators=[wtf.Required()], default='participant.html',
        description=u"Template with which a participant’s directory entry will be rendered.")
    properties = DictField(u"Properties")
