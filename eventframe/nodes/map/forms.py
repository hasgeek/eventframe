# -*- coding: utf-8 -*-

import wtforms
from eventframe.forms import Form, DictField, valid_name

__all__ = ['MapForm']


class MapForm(Form):
    name = wtforms.TextField(u"URL name", validators=[wtforms.validators.Required(), valid_name])
    title = wtforms.TextField(u"Title", validators=[wtforms.validators.Required()])
    list = wtforms.TextAreaField('Map markers', validators=[wtforms.validators.Required()],
        description=u'Enter each row as a JSON object with name, title, url, '
            u'latitude, longitude, zoomlevel and marker. '
            u'The URL, zoomlevel and marker can be null, others cannot.')
    properties = DictField(u"Properties")
