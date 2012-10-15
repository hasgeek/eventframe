# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from eventframe.forms import (Form, RichTextField, DictField, valid_name,
    tinymce_options, richtext_sanitize_tags, richtext_sanitize_attributes)

__all__ = ['FragmentForm']


class FragmentForm(Form):
    """
    A fragment form is like a content form but without a summary or template.
    """
    previous_id = wtf.HiddenField(u"Previous revision")
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    name = wtf.TextField(u"URL name", validators=[wtf.Required(), valid_name])
    content = RichTextField(u"Page content", linkify=False,
        tinymce_options=tinymce_options,
        sanitize_tags=richtext_sanitize_tags,
        sanitize_attributes=richtext_sanitize_attributes)
    properties = DictField(u"Properties")

    def validate_previous_id(self, field):
        if not field.data:
            field.data = None
        else:
            try:
                field.data = int(field.data)
            except ValueError:
                raise wtf.ValidationError(u"Unknown previous revision")

    def validate_name(self, field):
        # TODO
        pass
