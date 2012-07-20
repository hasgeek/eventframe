# -*- coding: utf-8 -*-

from flask import request, render_template
import flask.ext.wtf as wtf


def render_form(form, title, message='', formid='form', submit=u"Submit", cancel_url=None, tabs=[], ajax=False):
    multipart = False
    for field in form:
        if isinstance(field.widget, wtf.FileInput):
            multipart = True
    if request.is_xhr and ajax:
        return render_template('baseframe/ajaxform.html', form=form, title=title,
            message=message, formid=formid, submit=submit,
            cancel_url=cancel_url, multipart=multipart)
    else:
        return render_template('autoform.html', form=form, title=title,
            message=message, formid=formid, submit=submit,
            cancel_url=cancel_url, ajax=ajax, multipart=multipart, tabs=tabs)
