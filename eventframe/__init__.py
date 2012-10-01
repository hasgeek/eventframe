# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

from threading import Lock
from pytz import timezone
from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask.ext.themes import setup_themes
from flask.ext.lastuser import Lastuser
from flask.ext.lastuser.sqlalchemy import UserManager
from baseframe import baseframe, baseframe_js, baseframe_css, toastr_js, toastr_css
from coaster.app import SandboxedFlask, init_app
from eventframe.assets import ThemeAwareEnvironment, load_theme_assets
import eventframe.signals


# First, create a domain dispatcher that knows where to send each request

class DomainDispatcher(object):
    def __init__(self, hosts, app, eventapp):
        self.hosts = set(hosts)
        self.lock = Lock()
        self.app = app
        self.eventapp = eventapp

    def get_application(self, host):
        if ':' in host:
            host = host.split(':', 1)[0]
        with self.lock:
            if host in self.hosts:
                return self.app
            else:
                return self.eventapp

    def __call__(self, environ, start_response):
        app = self.get_application(environ['HTTP_HOST'])
        return app(environ, start_response)


# Second, make the main and event apps

app = Flask(__name__, instance_relative_config=True)
eventapp = SandboxedFlask(__name__, instance_relative_config=True, template_folder='themes-templates')
lastuser = Lastuser()


# Third, import models, nodes and views

import eventframe.models
import eventframe.nodes
eventframe.nodes.init()
import eventframe.views


# Fourth, setup baseframe, assets and theme assets on both apps

app.register_blueprint(baseframe)
eventapp.register_blueprint(baseframe)

assets = Environment(app)
eventassets = ThemeAwareEnvironment(eventapp)

js = Bundle(baseframe_js, toastr_js,
    filters='jsmin', output='js/packed.js')

css = Bundle(baseframe_css, toastr_css, 'css/app.css',
    filters='cssmin', output='css/packed.css')


def init_for(env):
    init_app(app, env)
    init_app(eventapp, env)
    app.config['tz'] = timezone(eventapp.config['TIMEZONE'])
    eventframe.models.db.init_app(app)
    eventframe.models.db.init_app(eventapp)
    lastuser.init_app(app)
    lastuser.init_usermanager(UserManager(eventframe.models.db, eventframe.models.User))
    assets.register('js_all', js)
    assets.register('css_all', css)
    eventassets.register('js_baseframe', baseframe_js)
    eventassets.register('css_baseframe', baseframe_css)

    setup_themes(eventapp, app_identifier='eventframe')
    setup_themes(app, app_identifier='eventframe')  # To list themes in the admin views
    for theme in eventapp.theme_manager.list_themes():
        load_theme_assets(eventassets, theme)

    return DomainDispatcher(app.config['ADMIN_HOSTS'], app, eventapp)
