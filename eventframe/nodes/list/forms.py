# -*- coding: utf-8 -*-

import wtforms
from eventframe.forms import Form, DictField, valid_name

__all__ = ['ListForm']


class ListForm(Form):
    name = wtforms.TextField("URL name", validators=[wtforms.validators.Required(), valid_name])
    title = wtforms.TextField("Title", validators=[wtforms.validators.Required()])
    list = wtforms.TextAreaField('Items', validators=[wtforms.validators.Required()],
        description='Enter each row as a JSON array with ["name", title", "url", "folder/node"]. '
            'For nodes in the root folder, use "/node". To not include a node, use "".')
    properties = DictField("Properties")
