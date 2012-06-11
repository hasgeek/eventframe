# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

import os.path
from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask.ext.themes import setup_themes, load_themes_from, packaged_themes_loader
from baseframe import baseframe, baseframe_js, baseframe_css
from coaster.app import configure

from threading import Lock


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


def theme_loader(app):
    """
    Look for site themes in a specific path
    """
    dir = app.config.get('THEMES_PATH')
    if dir and os.path.isdir(dir):
        return load_themes_from(dir)
    else:
        return ()

# Second, make the main and event apps and configure them

app = Flask(__name__, instance_relative_config=True)
eventapp = Flask(__name__, instance_relative_config=True)
configure(app, 'ENVIRONMENT')
configure(eventapp, 'ENVIRONMENT')


# Third, after config, import and configure the models and views

import eventframe.models
import eventframe.views

eventframe.models.db.init_app(app)
eventframe.models.db.init_app(eventapp)


# Fourth, setup baseframe and assets on both apps

app.register_blueprint(baseframe)
eventapp.register_blueprint(baseframe)

assets = Environment(app)
eventassets = Environment(eventapp)

js = Bundle(baseframe_js)
css = Bundle(baseframe_css,
             'css/app.css')
assets.register('js_all', js)
assets.register('css_all', css)
eventassets.register('js_all', js)
eventassets.register('css_all', css)

# TODO: Watch for side-effects before using this
# assets.set_url('http://localhost:8000/static')

setup_themes(eventapp,
    loaders=(packaged_themes_loader, theme_loader),
    app_identifier='eventframe')

# Finally, setup admin for the models on the main app

#from flask.ext import admin
#from flask.ext.admin.datastore.sqlalchemy import SQLAlchemyDatastore
#from eventframe.views.login import lastuser

#admin_datastore = SQLAlchemyDatastore(eventframe.models, eventframe.models.db.session)
#admin_blueprint = admin.create_admin_blueprint(admin_datastore,
#    view_decorator=lastuser.requires_permission('siteadmin'))

#app.register_blueprint(admin_blueprint, url_prefix='/admin')

application = DomainDispatcher(app.config['ADMIN_HOSTS'], app, eventapp)
