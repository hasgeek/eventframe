# -*- coding: utf-8 -*-

import simplejson as json
from coaster.utils import make_name
import wtforms
import wtforms.fields.html5
from baseframe.forms import Form, RichTextField, DateTimeField
from pytz import common_timezones

__all__ = ['Form', 'RichTextField', 'DateTimeField', 'DictField',
    'WebsiteForm', 'FolderForm', 'ImportForm', 'ConfirmForm',
    'timezone_list', 'tinymce_options', 'richtext_sanitize_tags', 'richtext_sanitize_attributes',
    'valid_name']

timezone_list = [(tz, tz) for tz in common_timezones]
tinymce_options = {
    'plugins': "autosave,advlist,fullscreen,inlinepopups,pagebreak,paste,searchreplace,table,wordcount",
    'theme_advanced_buttons1': "bold,italic,|,sup,sub,|,bullist,numlist,|,link,unlink,|,blockquote,image,|,removeformat,code,|,search,replace,|,fullscreen",
    'theme_advanced_buttons2': "tablecontrols",
    'theme_advanced_path': True,
    'valid_elements': "p,br,strong/b,em/i,sup,sub,h1,h2,h3,h4,h5,h6,ul,ol,li,a[!href|title|target|class],span[class],blockquote,pre,code,img[!src|alt|class|width|height|align],table[class],thead[class],tbody[class],tfoot[class],tr[class],th[class|colspan|rowspan],td[class|colspan|rowspan],iframe[!src|width|height|frameborder|allowfullscreen|class]",
    'table_styles': "Table=table;Striped=table table-striped;Bordered=table table-bordered;Condensed=table table-condensed",
    'table_cell_styles': "",
    'table_row_styles': ""
    }
richtext_sanitize_tags = ['p', 'br', 'strong', 'em', 'sup', 'sub', 'h3', 'h4', 'h5', 'h6',
                'ul', 'ol', 'li', 'a', 'span', 'blockquote', 'pre', 'code', 'img',
                'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'iframe']
richtext_sanitize_attributes = {'a': ['href', 'title', 'target', 'class'],
                                'span': ['class'],
                                'img': ['src', 'alt', 'class', 'width', 'height', 'align'],
                                'table': ['class'],
                                'thead': ['class'],
                                'tbody': ['class'],
                                'tfoot': ['class'],
                                'tr': ['class'],
                                'th': ['class', 'colspan', 'rowspan'],
                                'td': ['class', 'colspan', 'rowspan'],
                                'iframe': ['src', 'class', 'width', 'height', 'frameborder', 'allowfullscreen']}


def valid_name(form, field):
    field.data = make_name(field.data)


class HostnamesField(wtforms.fields.Field):
    widget = wtforms.widgets.TextInput()

    def __init__(self, label='', validators=None, **kwargs):
        super(HostnamesField, self).__init__(label, validators, **kwargs)

    def _value(self):
        if self.data:
            return ', '.join(self.data)
        else:
            return ''

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


class DictField(wtforms.fields.Field):
    widget = wtforms.widgets.TextArea()
    description = 'One per line, as {"key": "value"}'

    def __init__(self, *args, **kwargs):
        if not 'description' in kwargs:
            kwargs['description'] = self.description
        super(DictField, self).__init__(*args, **kwargs)

    def _value(self):
        if isinstance(self.data, dict):
            return '\r\n'.join([json.dumps({key: value}) for key, value in list(self.data.items())])
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
    title = wtforms.TextField("Title", validators=[wtforms.validators.Required()])
    name = wtforms.TextField("URL name", validators=[wtforms.validators.Required(), valid_name])
    url = wtforms.fields.html5.URLField("Website URL", validators=[wtforms.validators.Required()])
    hostnames = HostnamesField("Hostnames", validators=[wtforms.validators.Required()],
        description="Hostnames at which this website will be accessed, comma separated")
    theme = wtforms.SelectField("Website theme", validators=[wtforms.validators.Required()])
    typekit_code = wtforms.TextField("Typekit code")
    googleanalytics_code = wtforms.TextField("Google Analytics code")

    def validate_name(self, field):
        # TODO: Ensure name is unique
        pass

    def validate_hostnames(self, field):
        # TODO: Validate that names match hostname:port
        pass


class FolderForm(Form):
    name = wtforms.TextField("URL name", validators=[wtforms.validators.Optional(), valid_name],
        description="Folder name as it appears in the URL (without slashes)")
    title = wtforms.TextField("Title",
        description="Folder title, used in the per-folder blog feed")
    theme = wtforms.SelectField("Theme")

    def validate_name(self, field):
        # TODO
        pass


class ImportForm(Form):
    import_file = wtforms.FileField("Upload file", validators=[wtforms.validators.Required()])
    import_updated = wtforms.BooleanField("Only import newer nodes", default=True,
        description="Nodes that are newer locally will not be imported")


class ConfirmForm(Form):
    pass  # Only needed for CSRF confirmation


class FileFolderForm(Form):
    name = wtforms.TextField("URL name", validators=[wtforms.validators.Required(), valid_name])
    title = wtforms.TextField("Title", validators=[wtforms.validators.Required()])
    properties = DictField("Properties")
