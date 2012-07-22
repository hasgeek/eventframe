# -*- coding: utf-8 -*-

from flask import current_app, request, render_template
import flask.ext.wtf as wtf


def render_form(form, title, message='', formid='form', submit=u"Submit", cancel_url=None, tabs=[], node=None, ajax=False):
    multipart = False
    for field in form:
        if isinstance(field.widget, wtf.FileInput):
            multipart = True
    if request.is_xhr and ajax:
        return render_template('baseframe/ajaxform.html', form=form, title=title,
            message=message, formid=formid, submit=submit,
            cancel_url=cancel_url, multipart=multipart, node=node)
    else:
        return render_template('autoform.html', form=form, title=title,
            message=message, formid=formid, submit=submit,
            cancel_url=cancel_url, ajax=ajax, multipart=multipart,
            tabs=tabs, node=node)


def stream_template(template_name, **context):
    current_app.update_template_context(context)
    t = current_app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.disable_buffering()
    return rv
