# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive


from threading import Lock
from pytz import timezone
from flask import Flask
from flask_assets import Bundle
from flask_themes import setup_themes
from flask_lastuser import Lastuser
from flask_lastuser.sqlalchemy import UserManager
import baseframe
from flask_migrate import Migrate
from coaster.app import SandboxedFlask, init_app

from .assets import ThemeAwareEnvironment, load_theme_assets
from ._version import __version__

# First, create a domain dispatcher that knows where to send each request


class DomainDispatcher(object):
    def __init__(self, hosts, app, eventapp):
        self.hosts = set(hosts)
        self.lock = Lock()
        self.app = app
        self.eventapp = eventapp

    def get_application(self, host):
        if ':' in host:  # Remove port number
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

version = baseframe.Version(__version__)
app = Flask(__name__, instance_relative_config=True)
eventapp = SandboxedFlask(__name__, instance_relative_config=True, template_folder='themes-templates')
lastuser = Lastuser()

# Third, import models, nodes and views

import eventframe.models
import eventframe.nodes
eventframe.nodes.init()
import eventframe.views

from eventframe.models import db  # NOQA

# Fourth, setup baseframe, assets and theme assets on both apps
baseframe.assets['eventframe.css'][version] = 'css/app.css'
eventassets = ThemeAwareEnvironment(eventapp)


init_app(app)
init_app(eventapp)
app.config['tz'] = timezone(eventapp.config['TIMEZONE'])
eventframe.models.db.init_app(app)
eventframe.models.db.init_app(eventapp)
migrate = Migrate(app, eventframe.models.db)
baseframe.baseframe.init_app(app, requires=['baseframe', 'toastr', 'eventframe'])
baseframe.baseframe.init_app(eventapp, requires=['baseframe'], assetenv=eventassets)
eventapp.assets = eventassets  # Replace baseframe-provided Environment with ThemeAwareEnvironment

lastuser.init_app(app)
lastuser.init_usermanager(UserManager(eventframe.models.db, eventframe.models.User))
eventassets.register('js_baseframe',
    Bundle(baseframe.assets.require('baseframe.js'), filters='uglipyjs', output='js/packed.js'))
eventassets.register('css_baseframe',
    Bundle(baseframe.assets.require('baseframe.css'), filters='cssmin', output='css/packed.css'))

setup_themes(eventapp, app_identifier='eventframe')
setup_themes(app, app_identifier='eventframe')  # To list themes in the admin views
for theme in eventapp.theme_manager.list_themes():
    load_theme_assets(eventassets, theme)

debug_app = DomainDispatcher(app.config['ADMIN_HOSTS'], app, eventapp)
