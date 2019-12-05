# -*- coding: utf-8 -*-

import wtforms
from eventframe.forms import (Form, RichTextField, DictField, valid_name,
    tinymce_options, richtext_sanitize_tags, richtext_sanitize_attributes)

__all__ = ['ContentForm']


class ContentForm(Form):
    previous_id = wtforms.HiddenField("Previous revision")
    title = wtforms.TextField("Title", validators=[wtforms.validators.Required()])
    name = wtforms.TextField("URL name", validators=[wtforms.validators.Optional(), valid_name])
    author = wtforms.TextField("Author (optional)", validators=[wtforms.validators.Length(max=40)],
        description="Name of the author. Will default to your name if blank")
    description = wtforms.TextAreaField("Summary", description="Summary of this page")
    content = RichTextField("Page content", linkify=False,
        tinymce_options=tinymce_options,
        sanitize_tags=richtext_sanitize_tags,
        sanitize_attributes=richtext_sanitize_attributes)
    template = wtforms.TextField("Template", validators=[wtforms.validators.Required()], default='page.html.jinja2',
        description="Template with which this page will be rendered.")
    properties = DictField("Properties")

    def validate_previous_id(self, field):
        if not field.data:
            field.data = None
        else:
            try:
                field.data = int(field.data)
            except ValueError:
                raise wtforms.ValidationError("Unknown previous revision")

    def validate_name(self, field):
        # TODO
        pass

    def validate_author(self, field):
        if not field.data:
            field.data = None
