# -*- coding: utf-8 -*-

from coaster import make_name
import flask.ext.wtf as wtf
from baseframe.forms import Form, RichTextField

__all__ = ['WebsiteForm', 'FolderForm', 'ContentForm', 'FragmentForm', 'ImportForm', 'RedirectForm']


def valid_name(form, field):
    field.data = make_name(field.data)


class HostnamesField(wtf.Field):
    widget = wtf.TextInput()

    def __init__(self, label='', validators=None, **kwargs):
        super(HostnamesField, self).__init__(label, validators, **kwargs)

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = list(self._remove_duplicates([x.strip() for x in valuelist[0].split(',')]))
        else:
            self.data = []

    @classmethod
    def _remove_duplicates(cls, seq):
        """Remove duplicates and convert to lowercase"""
        d = {}
        for item in seq:
            item = item.lower()
            if item not in d:
                d[item] = True
                yield item


class WebsiteForm(Form):
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    name = wtf.TextField(u"URL name", validators=[wtf.Required()])
    url = wtf.html5.URLField(u"Website URL", validators=[wtf.Required()])
    hostnames = HostnamesField(u"Hostnames", validators=[wtf.Required()],
        description=u"Hostnames at which this website will be accessed, comma separated")
    theme = wtf.SelectField(u"Website theme", validators=[wtf.Required()])
    typekit_code = wtf.TextField(u"Typekit code")
    googleanalytics_code = wtf.TextField(u"Google Analytics code")

    def validate_name(self, field):
        # TODO: Ensure name is unique
        pass

    def validate_hostnames(self, field):
        # TODO: Validate that names match hostname:port
        pass


class FolderForm(Form):
    name = wtf.TextField(u"URL name",
        description=u"Folder name as it appears in the URL (without slashes)")
    title = wtf.TextField(u"Title",
        description=u"Folder title, used in the per-folder feed")
    theme = wtf.SelectField(u"Theme")

    def validate_name(self, field):
        # TODO
        pass


class ContentForm(Form):
    previous_id = wtf.HiddenField(u"Previous revision")
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    name = wtf.TextField(u"URL name")
    description = wtf.TextAreaField(u"Summary", description=u"Summary of this page")
    content = RichTextField(u"Page content")
    template = wtf.TextField("Template", validators=[wtf.Required()], default='page.html',
        description=u"Template with which this page will be rendered.")

    def validate_name(self, field):
        # TODO
        pass


class FragmentForm(Form):
    """
    A fragment form is like a content form but without a summary or template.
    """
    previous_id = wtf.HiddenField(u"Previous revision")
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    name = wtf.TextField(u"URL name", validators=[wtf.Required()])
    content = RichTextField(u"Page content")

    def validate_name(self, field):
        # TODO
        pass


class RedirectForm(Form):
    name = wtf.TextField(u"URL name", validators=[])
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    redirect_url = wtf.TextField("Redirect URL", validators=[wtf.Required()])

    def validate_name(self, field):
        # TODO
        pass


class ImportForm(Form):
    import_file = wtf.FileField(u"Upload file", validators=[wtf.Required()])
    import_updated = wtf.BooleanField(u"Only import newer nodes", default=True,
        description=u"Nodes that are newer locally will not be imported")
