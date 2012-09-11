# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from eventframe.forms import Form, DictField, valid_name

__all__ = ['ListForm']


class ListForm(Form):
    name = wtf.TextField(u"URL name", validators=[wtf.Required(), valid_name])
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    list = wtf.TextAreaField('Items', validators=[wtf.Required()],
        description=u'Enter each row as a JSON array with ["name", title", "url", "folder/node"]. '
            u'For nodes in the root folder, use "/node". To not include a node, use "".')
    properties = DictField(u"Properties")
