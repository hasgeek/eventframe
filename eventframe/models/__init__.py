# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from eventframe import app, eventapp
from coaster.sqlalchemy import IdMixin, TimestampMixin, BaseMixin, BaseNameMixin

db = SQLAlchemy()
db.init_app(app)
db.init_app(eventapp)

from eventframe.models.user import *
