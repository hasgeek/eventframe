# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from eventframe.forms import DictField
from eventframe.nodes.content import ContentForm

__all__ = ['FunnelLinkForm']


class FunnelLinkForm(ContentForm):
    funnel_name = wtf.TextField(u"Funnel name", validators=[wtf.Required()],
        description=u"URL name of the event in the HasGeek funnel")
    properties = DictField(u"Properties")
