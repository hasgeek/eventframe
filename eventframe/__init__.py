# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask.ext.themes import setup_themes
from werkzeug.exceptions import NotFound
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
                # TODO: Check if host matches known hosts for event websites
                # and return either eventapp or NotFound()
                # Also stick this domain match into `g` or somewhere that
                # the route handler can find
                return self.eventapp
                return NotFound()

    def __call__(self, environ, start_response):
        app = self.get_application(environ['HTTP_HOST'])
        return app(environ, start_response)


# Second, make the main and event apps and configure them

app = Flask(__name__, instance_relative_config=True)
eventapp = Flask(__name__, instance_relative_config=True)
configure(app, 'ENVIRONMENT')
configure(eventapp, 'ENVIRONMENT')

# Third, after config, import and configure the models and views

import eventframe.models
import eventframe.views

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

setup_themes(eventapp)

# Finally, setup admin for the models on the main app

from flask.ext import admin
from flask.ext.admin.datastore.sqlalchemy import SQLAlchemyDatastore
from eventframe.views.login import lastuser

admin_datastore = SQLAlchemyDatastore(eventframe.models, eventframe.models.db.session)
admin_blueprint = admin.create_admin_blueprint(admin_datastore,
    view_decorator=lastuser.requires_permission('siteadmin'))

app.register_blueprint(admin_blueprint, url_prefix='/admin')

application = DomainDispatcher(app.config['ADMIN_HOSTS'], app, eventapp)
