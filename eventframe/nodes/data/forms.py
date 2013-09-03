# -*- coding: utf-8 -*-

import simplejson
import wtforms
from eventframe.forms import Form, DictField, valid_name

__all__ = ['DataForm']


class DataForm(Form):
    name = wtforms.TextField(u"URL name", validators=[wtforms.validators.Required(), valid_name])
    title = wtforms.TextField(u"Title", validators=[wtforms.validators.Required()])
    data = wtforms.TextAreaField(u"Data", validators=[wtforms.validators.Required()],
        description=u"Enter JSON data")
    properties = DictField(u"Properties")

    def validate_data(self, field):
        # Check for exceptions when loading data
        parsed = simplejson.loads(field.data, use_decimal=True)
        if not isinstance(parsed, dict):
            raise wtforms.ValidationError(u'This is not a valid JSON object. Use {"key": value, ...}')
