# -*- coding: utf-8 -*-

import wtforms
from eventframe.forms import Form, DictField, valid_name

__all__ = ['RedirectForm']


class RedirectForm(Form):
    name = wtforms.TextField("URL name", validators=[wtforms.validators.Optional(), valid_name])
    title = wtforms.TextField("Title", validators=[wtforms.validators.Required()])
    redirect_url = wtforms.TextField("Redirect URL", validators=[wtforms.validators.Required()])
    properties = DictField("Properties")

    def validate_name(self, field):
        if field.data == '/':
            field.data = ''
        # TODO
        pass
