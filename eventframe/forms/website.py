# -*- coding: utf-8 -*-

import simplejson as json
from coaster import make_name
import flask.ext.wtf as wtf
from baseframe.forms import Form, RichTextField, DateTimeField
from pytz import common_timezones

__all__ = ['WebsiteForm', 'FolderForm', 'ContentForm', 'FragmentForm', 'ImportForm', 'RedirectForm',
    'ConfirmForm', 'ListForm', 'FunnelLinkForm', 'MapForm', 'ParticipantListForm', 'EventForm']

timezone_list = [(tz, tz) for tz in common_timezones]

richtext_buttons1 = "bold,italic,|,sup,sub,|,bullist,numlist,|,link,unlink,|,blockquote,image,|,removeformat,code"
richtext_valid_elements = "p,br,strong/b,em/i,sup,sub,h3,h4,h5,h6,ul,ol,li,a[!href|title|target],blockquote,code,img[!src|alt|class|width|height|align]"
richtext_sanitize_tags = ['p', 'br', 'strong', 'em', 'sup', 'sub', 'h3', 'h4', 'h5', 'h6',
                'ul', 'ol', 'li', 'a', 'blockquote', 'code', 'img']
richtext_sanitize_attributes = {'a': ['href', 'title', 'target'],
                                'img': ['src', 'alt', 'class', 'width', 'height', 'align']}


def valid_name(form, field):
    field.data = make_name(field.data)


class HostnamesField(wtf.fields.Field):
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

    @staticmethod
    def _remove_duplicates(seq):
        """Remove duplicates and convert to lowercase"""
        d = {}
        for item in seq:
            item = item.lower()
            if item not in d:
                d[item] = True
                yield item


class DictField(wtf.fields.Field):
    widget = wtf.TextArea()
    description = u'One per line, as {"key": "value"}'

    def __init__(self, *args, **kwargs):
        if not 'description' in kwargs:
            kwargs['description'] = self.description
        super(DictField, self).__init__(*args, **kwargs)

    def _value(self):
        if isinstance(self.data, dict):
            return '\r\n'.join([json.dumps({key: value}) for key, value in self.data.items()])
        return ''

    def process_formdata(self, valuelist):
        self.data = {}
        if valuelist:
            for row in valuelist[0].split('\n'):
                if row:
                    rowdata = json.loads(row)
                    if isinstance(rowdata, dict):
                        self.data.update(rowdata)


class WebsiteForm(Form):
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    name = wtf.TextField(u"URL name", validators=[wtf.Required(), valid_name])
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
    name = wtf.TextField(u"URL name", validators=[wtf.Optional(), valid_name],
        description=u"Folder name as it appears in the URL (without slashes)")
    title = wtf.TextField(u"Title",
        description=u"Folder title, used in the per-folder blog feed")
    theme = wtf.SelectField(u"Theme")

    def validate_name(self, field):
        # TODO
        pass


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


class FunnelLinkForm(ContentForm):
    funnel_name = wtf.TextField(u"Funnel name", validators=[wtf.Required()],
        description=u"URL name of the event in the HasGeek funnel")
    properties = DictField(u"Properties")


class FragmentForm(Form):
    """
    A fragment form is like a content form but without a summary or template.
    """
    previous_id = wtf.HiddenField(u"Previous revision")
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    name = wtf.TextField(u"URL name", validators=[wtf.Required(), valid_name])
    content = RichTextField(u"Page content", linkify=False,
        buttons1=richtext_buttons1,
        valid_elements=richtext_valid_elements,
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


class RedirectForm(Form):
    name = wtf.TextField(u"URL name", validators=[wtf.Optional(), valid_name])
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    redirect_url = wtf.TextField(u"Redirect URL", validators=[wtf.Required()])
    properties = DictField(u"Properties")

    def validate_name(self, field):
        # TODO
        pass


class ImportForm(Form):
    import_file = wtf.FileField(u"Upload file", validators=[wtf.Required()])
    import_updated = wtf.BooleanField(u"Only import newer nodes", default=True,
        description=u"Nodes that are newer locally will not be imported")


class ConfirmForm(Form):
    pass  # Only needed for CSRF confirmation


class ListForm(Form):
    name = wtf.TextField(u"URL name", validators=[wtf.Required(), valid_name])
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    list = wtf.TextAreaField('Items', validators=[wtf.Required()],
        description=u'Enter each row as a JSON array with ["name", title", "url", "folder/node"]. '
            u'For nodes in the root folder, use "/node". To not include a node, use "".')
    properties = DictField(u"Properties")


class MapForm(Form):
    name = wtf.TextField(u"URL name", validators=[wtf.Required(), valid_name])
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    list = wtf.TextAreaField('Map markers', validators=[wtf.Required()],
        description=u'Enter each row as a JSON object with name, title, url, '
            u'latitude, longitude, zoomlevel and marker. '
            u'The URL, zoomlevel and marker can be null, others cannot.')
    properties = DictField(u"Properties")


class FileFolderForm(Form):
    name = wtf.TextField(u"URL name", validators=[wtf.Required(), valid_name])
    title = wtf.TextField(u"Title", validators=[wtf.Required()])
    properties = DictField(u"Properties")


class ParticipantListForm(ContentForm):
    source = wtf.SelectField(u"Data Source", choices=[
        ('', ''), ('doattend', 'DoAttend')],
        description=u"Source from which the participant list will be retrieved.")
    sourceid = wtf.TextField(u"Event id",
        description=u"Id of this event at the selected data source.")
    api_key = wtf.TextField(u"API Key",
        description=u"API key to retrieve data from the selected data source.")
    participant_template = wtf.TextField("Participant template",
        validators=[wtf.Required()], default='participant.html',
        description=u"Template with which a participant’s directory entry will be rendered.")
    properties = DictField(u"Properties")


class EventForm(ContentForm):
    start_datetime = DateTimeField(u"Start date/time", validators=[wtf.Required()])
    end_datetime = DateTimeField(u"End date/time", validators=[wtf.Required()])
    timezone = wtf.SelectField(u"Timezone", choices=timezone_list, validators=[wtf.Required()])
    location_name = wtf.TextField(u"Location name", validators=[wtf.Required()])
    location_address = wtf.TextField(u"Address", validators=[wtf.Required()])
    map = wtf.QuerySelectField(u"Map", get_label='title', allow_blank=True)
    mapmarker = wtf.TextField(u"Map marker")
    capacity = wtf.IntegerField(u"Capacity", validators=[wtf.Required()])
    allow_waitlisting = wtf.BooleanField(u"Allow wait-listing if over capacity", default=False)
    allow_maybe = wtf.BooleanField(u"Allow “Maybe” responses", default=True)
    participant_list = wtf.QuerySelectField(u"Participant list", get_label='title', allow_blank=True)
    properties = DictField(u"Properties")
