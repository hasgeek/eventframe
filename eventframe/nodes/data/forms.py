# -*- coding: utf-8 -*-

import simplejson
import flask.ext.wtf as wtf
from eventframe.forms import Form, DictField, valid_name

__all__ = ['DataForm']


class DataForm(Form):
    name = wtf.TextField(u"URL name", validators=[wtf.Required(), valid_name])
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    data = wtf.TextAreaField(u"Data", validators=[wtf.Required()],
        description=u"Enter JSON data")
    properties = DictField(u"Properties")

    def validate_data(self, field):
        # Check for exceptions when loading data
        parsed = simplejson.loads(field.data, use_decimal=True)
        if not isinstance(parsed, dict):
            raise wtf.ValidationError(u'This is not a valid JSON object. Use {"key": value, ...}')
