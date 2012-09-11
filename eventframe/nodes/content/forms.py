# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from eventframe.forms import (Form, RichTextField, DictField, valid_name,
    richtext_buttons1, richtext_valid_elements, richtext_sanitize_tags,
    richtext_sanitize_attributes)

__all__ = ['ContentForm']


class ContentForm(Form):
    previous_id = wtf.HiddenField(u"Previous revision")
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    name = wtf.TextField(u"URL name", validators=[wtf.Optional(), valid_name])
    description = wtf.TextAreaField(u"Summary", description=u"Summary of this page")
    content = RichTextField(u"Page content", linkify=False,
        buttons1=richtext_buttons1,
        valid_elements=richtext_valid_elements,
        sanitize_tags=richtext_sanitize_tags,
        sanitize_attributes=richtext_sanitize_attributes)
    template = wtf.TextField("Template", validators=[wtf.Required()], default='page.html',
        description=u"Template with which this page will be rendered.")
    properties = DictField(u"Properties")

    def validate_previous_id(self, field):
        if not field.data:
            field.data = None
        else:
            try:
                field.data = int(field.data)
            except ValueError:
                raise wtf.ValidationError("Unknown previous revision")

    def validate_name(self, field):
        # TODO
        pass


