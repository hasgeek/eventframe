# -*- coding: utf-8 -*-

import wtforms
from eventframe.forms import Form, DictField, valid_name

__all__ = ['MapForm']


class MapForm(Form):
    name = wtforms.TextField("URL name", validators=[wtforms.validators.Required(), valid_name])
    title = wtforms.TextField("Title", validators=[wtforms.validators.Required()])
    list = wtforms.TextAreaField('Map markers', validators=[wtforms.validators.Required()],
        description='Enter each row as a JSON object with name, title, url, '
            'latitude, longitude, zoomlevel and marker. '
            'The URL, zoomlevel and marker can be null, others cannot.')
    properties = DictField("Properties")
