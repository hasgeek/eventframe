# -*- coding: utf-8 -*-

from pytz import utc, timezone
from flask import g
from eventframe import app, eventapp
from eventframe.models import Folder, Node
from eventframe.nodes.post import rootfeed, folderfeed
from eventframe.nodes.fragment import Fragment

tz = timezone(eventapp.config['TIMEZONE'])


@app.template_filter('shortdate')
@eventapp.template_filter('shortdate')
def shortdate(date):
    return utc.localize(date).astimezone(tz).strftime('%b %e')


@app.template_filter('longdate')
@eventapp.template_filter('longdate')
def longdate(date):
    return utc.localize(date).astimezone(tz).strftime('%B %e, %Y')


def feedhelper(folder=None, limit=20):
    if folder is None:
        folder = Folder.query.filter_by(name=u'', website=g.website).first()
    if folder.name == '':
        return rootfeed(folder.website, limit)
    else:
        return folderfeed(folder, limit)


def fragmenthelper(folder, fragment):
    folder = Folder.query.filter_by(name=folder, website=g.website).first()
    fragment = Fragment.query.filter_by(name=fragment, folder=folder).first()
    return fragment


def nodehelper(folder=None, node=None, path=None):
    if path:
        if "/" in path:
            folder, node = path.split('/', 1)
        else:
            node = path
    if folder is None:
        folder = g.folder
    else:
        folder = Folder.query.filter_by(name=folder, website=g.website).first()
    if node is None:
        return None
    return Node.query.filter_by(name=node, folder=folder).first()


@eventapp.context_processor
def helpers():
    website = g.website if hasattr(g, 'website') else None
    if website:
        return {
            'website': website,
            '_theme': g.folder.theme if hasattr(g, 'folder') else website.theme,
            'feed': feedhelper,
            'fragment': fragmenthelper,
            'getnode': nodehelper,
        }
    else:
        # This is called when showing error pages.
        return {
            'website': None,
            '_theme': '',
            'feed': None,
            'fragment': None,
            'getnode': None,
        }
