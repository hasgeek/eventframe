# -*- coding: utf-8 -*-

from pytz import utc, timezone
from flask import g
from eventframe import app, eventapp
from eventframe.models import Folder, Fragment
from eventframe.views.website import rootfeed, folderfeed

tz = timezone(eventapp.config['TIMEZONE'])


@app.template_filter('shortdate')
@eventapp.template_filter('shortdate')
def shortdate(date):
    return utc.localize(date).astimezone(tz).strftime('%b %e')


@app.template_filter('longdate')
@eventapp.template_filter('longdate')
def longdate(date):
    return utc.localize(date).astimezone(tz).strftime('%B %e, %Y')


def feedhelper(folder=None):
    if folder is None:
        folder = Folder.query.filter_by(name=u'', website=g.website).first()
    if folder.name == '':
        return rootfeed(folder.website)
    else:
        return folderfeed(folder)


def fragmenthelper(folder, fragment):
    folder = Folder.query.filter_by(name=folder, website=g.website).first()
    fragment = Fragment.query.filter_by(name=fragment, folder=folder).first()
    return fragment


@eventapp.context_processor
def helpers():
    website = g.website if hasattr(g, 'website') else None
    if website:
        return {
            'website': website,
            '_theme': g.folder.theme if hasattr(g, 'folder') else website.theme,
            'feed': feedhelper,
            'fragment': fragmenthelper,
        }
    else:
        return {}
