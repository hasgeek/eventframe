# -*- coding: utf-8 -*-

from pytz import utc, timezone
from flask import g
from eventframe import app, eventapp
from eventframe.models import Folder, Page
from eventframe.views.website import get_website, rootfeed, folderfeed

tz = timezone(eventapp.config['TIMEZONE'])


@app.template_filter('shortdate')
@eventapp.template_filter('shortdate')
def shortdate(date):
    return utc.localize(date).astimezone(tz).strftime('%b %e')


@app.template_filter('longdate')
@eventapp.template_filter('longdate')
def longdate(date):
    return utc.localize(date).astimezone(tz).strftime('%B %e, %Y')


def feedhelper(folder):
    if folder.name == '':
        return rootfeed(folder.website)
    else:
        return folderfeed(folder)


def pagehelper(folder, page):
    folder = Folder.query.filter_by(name=folder, website=g.website).first()
    page = Page.query.filter_by(name=page, folder=folder).first()
    return page


@eventapp.context_processor
@get_website
def helpers(website):
    return {
        'website': website,
        '_theme': g.folder.theme if hasattr(g, 'folder') else website.theme,
        'feed': feedhelper,
        'fragment': pagehelper,
    }
