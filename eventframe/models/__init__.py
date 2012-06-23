# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from coaster.sqlalchemy import TimestampMixin, BaseMixin, BaseNameMixin, BaseScopedNameMixin

db = SQLAlchemy()

from eventframe.models.user import *
from eventframe.models.website import *
from eventframe.models.content import *
from eventframe.models.list import *
