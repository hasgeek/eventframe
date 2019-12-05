# -*- coding: utf-8 -*-

import wtforms
from eventframe.forms import DictField
from eventframe.nodes.content import ContentForm

__all__ = ['ParticipantListForm']


class ParticipantListForm(ContentForm):
    source = wtforms.SelectField("Data Source", choices=[
        ('', ''), ('doattend', 'DoAttend')],
        description="Source from which the participant list will be retrieved.")
    sourceid = wtforms.TextField("Event id",
        description="Id of this event at the selected data source.")
    api_key = wtforms.TextField("API Key",
        description="API key to retrieve data from the selected data source.")
    participant_template = wtforms.TextField("Participant template",
        validators=[wtforms.validators.Required()], default='participant.html.jinja2',
        description="Template with which a participant’s directory entry will be rendered.")
    properties = DictField("Properties")
