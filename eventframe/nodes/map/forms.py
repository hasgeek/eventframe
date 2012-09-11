# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from eventframe.forms import Form, DictField, valid_name

__all__ = ['MapForm']


class MapForm(Form):
    name = wtf.TextField(u"URL name", validators=[wtf.Required(), valid_name])
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    list = wtf.TextAreaField('Map markers', validators=[wtf.Required()],
        description=u'Enter each row as a JSON object with name, title, url, '
            u'latitude, longitude, zoomlevel and marker. '
            u'The URL, zoomlevel and marker can be null, others cannot.')
    properties = DictField(u"Properties")
