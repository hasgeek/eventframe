# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from coaster.sqlalchemy import TimestampMixin, BaseMixin, BaseNameMixin, BaseScopedNameMixin, BaseScopedIdMixin

db = SQLAlchemy()

from eventframe.models.user import *
from eventframe.models.website import *
