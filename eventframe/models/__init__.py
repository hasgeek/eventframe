# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from coaster.sqlalchemy import BaseMixin, BaseNameMixin, BaseScopedNameMixin, BaseScopedIdNameMixin

db = SQLAlchemy()

from eventframe.models.user import *
from eventframe.models.website import *
