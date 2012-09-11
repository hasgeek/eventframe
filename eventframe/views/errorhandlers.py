# -*- coding: utf-8 -*-

from flask.ext.themes import get_theme, render_theme_template
from eventframe import eventapp
from eventframe.nodes import get_website


@eventapp.errorhandler(404)
@get_website
def error404(website, e):
    theme = get_theme(website.theme)
    return render_theme_template(theme, '404.html'), 404


@eventapp.errorhandler(403)
@get_website
def error403(website, e):
    theme = get_theme(website.theme)
    return render_theme_template(theme, '403.html'), 403


@eventapp.errorhandler(500)
@get_website
def error500(website, e):
    theme = get_theme(website.theme)
    return render_theme_template(theme, '500.html'), 500
