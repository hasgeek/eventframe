# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

from threading import Lock
from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask.ext.themes import setup_themes
from baseframe import baseframe, baseframe_js, baseframe_css
from coaster.app import configure
from eventframe.assets import ThemeAwareEnvironment, load_theme_assets


# First, create a domain dispatcher that knows where to send each request

class DomainDispatcher(object):
    def __init__(self, hosts, app, eventapp):
        self.hosts = set(hosts)
        self.lock = Lock()
        self.app = app
        self.eventapp = eventapp

    def get_application(self, host):
        with self.lock:
            if host in self.hosts:
                return self.app
            else:
                return self.eventapp

    def __call__(self, environ, start_response):
        app = self.get_application(environ['HTTP_HOST'])
        return app(environ, start_response)


# Second, make the main and event apps and configure them

app = Flask(__name__, instance_relative_config=True)
eventapp = Flask(__name__, instance_relative_config=True, template_folder='themes-templates')
configure(app, 'ENVIRONMENT')
configure(eventapp, 'ENVIRONMENT')


# Third, after config, import and configure the models and views

import eventframe.models
import eventframe.views

eventframe.models.db.init_app(app)
eventframe.models.db.init_app(eventapp)


# Fourth, setup baseframe, assets and theme assets on both apps

app.register_blueprint(baseframe)
eventapp.register_blueprint(baseframe)

assets = Environment(app)
eventassets = ThemeAwareEnvironment(eventapp)

js = Bundle(baseframe_js)
css = Bundle(baseframe_css,
             'css/app.css')
assets.register('js_all', js)
assets.register('css_all', css)
eventassets.register('js_baseframe', baseframe_js)
eventassets.register('css_baseframe', baseframe_css)

setup_themes(eventapp, app_identifier='eventframe')
for theme in eventapp.theme_manager.list_themes():
    load_theme_assets(eventassets, theme)

# Finally, setup admin for the models on the main app

eventframe.views.admin.admin.init_app(app)
eventframe.views.admin.init_model_views()

application = DomainDispatcher(app.config['ADMIN_HOSTS'], app, eventapp)
