# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from eventframe.forms import Form, DictField, valid_name

__all__ = ['RedirectForm']


class RedirectForm(Form):
    name = wtf.TextField(u"URL name", validators=[wtf.Optional(), valid_name])
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    redirect_url = wtf.TextField(u"Redirect URL", validators=[wtf.Required()])
    properties = DictField(u"Properties")

    def validate_name(self, field):
        if field.data == u'/':
            field.data = u''
        # TODO
        pass
