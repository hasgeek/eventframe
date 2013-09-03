# -*- coding: utf-8 -*-

import wtforms
from eventframe.forms import Form, DictField, valid_name

__all__ = ['RedirectForm']


class RedirectForm(Form):
    name = wtforms.TextField(u"URL name", validators=[wtforms.validators.Optional(), valid_name])
    title = wtforms.TextField(u"Title", validators=[wtforms.validators.Required()])
    redirect_url = wtforms.TextField(u"Redirect URL", validators=[wtforms.validators.Required()])
    properties = DictField(u"Properties")

    def validate_name(self, field):
        if field.data == u'/':
            field.data = u''
        # TODO
        pass
