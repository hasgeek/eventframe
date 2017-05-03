# -*- coding: utf-8 -*-

from flask_lastuser.sqlalchemy import UserBase
from eventframe.models import db

__all__ = ['User']


class User(UserBase, db.Model):
    __tablename__ = 'user'
