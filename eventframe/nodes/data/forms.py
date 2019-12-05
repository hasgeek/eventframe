# -*- coding: utf-8 -*-

import simplejson
import wtforms
from eventframe.forms import Form, DictField, valid_name

__all__ = ['DataForm']


class DataForm(Form):
    name = wtforms.TextField("URL name", validators=[wtforms.validators.Required(), valid_name])
    title = wtforms.TextField("Title", validators=[wtforms.validators.Required()])
    data = wtforms.TextAreaField("Data", validators=[wtforms.validators.Required()],
        description="Enter JSON data")
    properties = DictField("Properties")

    def validate_data(self, field):
        # Check for exceptions when loading data
        parsed = simplejson.loads(field.data, use_decimal=True)
        if not isinstance(parsed, dict):
            raise wtforms.ValidationError('This is not a valid JSON object. Use {"key": value, ...}')
