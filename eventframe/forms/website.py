# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from baseframe.forms import Form, RichTextField, DateTimeInput

__all__ = ['WebsiteForm', 'HostnameForm', 'FolderForm', 'PageForm']


class WebsiteForm(Form):
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    name = wtf.TextField(u"URL name", validators=[wtf.Required()])
    url = wtf.html5.URLField(u"Website URL", validators=[wtf.Required()])
    theme = wtf.SelectField(u"Website theme", validators=[wtf.Required()])
    typekit_code = wtf.TextField(u"Typekit code")
    googleanalytics_code = wtf.TextField(u"Google Analytics code")

    def validate_name(self, field):
        # TODO: Ensure name is unique
        pass


class HostnameForm(Form):
    name = wtf.TextField(u"Hostname", validators=[wtf.Required()],
        description=u"Use hostname and port, like example.com:80")

    def validate_name(self, field):
        # TODO
        pass


class FolderForm(Form):
    name = wtf.TextField(u"URL name",
        description=u"Folder name")
    theme = wtf.SelectField(u"Theme")

    def validate_name(self, field):
        # TODO
        pass


class PageForm(Form):
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    name = wtf.TextField(u"URL name")
    datetime = wtf.DateTimeField(u"Publish datetime", widget=DateTimeInput(), validators=[wtf.Required()])
    blog = wtf.BooleanField("Is this a blog entry?")
    description = wtf.TextAreaField(u"Summary", description=u"Summary of this page")
    content = RichTextField(u"Page content", validators=[wtf.Required()])
    fragment = wtf.BooleanField("Is this a page fragment?")
    template = wtf.TextField("Template", validators=[wtf.Required()],
        description=u"Template with which this page will be rendered.")
