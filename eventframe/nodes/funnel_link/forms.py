# -*- coding: utf-8 -*-

import wtforms
from eventframe.forms import DictField
from eventframe.nodes.content import ContentForm

__all__ = ['FunnelLinkForm']


class FunnelLinkForm(ContentForm):
    funnel_name = wtforms.TextField("Funnel name", validators=[wtforms.validators.Required()],
        description="URL name of the event in the HasGeek funnel")
    properties = DictField("Properties")
