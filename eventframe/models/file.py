# -*- coding: utf-8 -*-

from eventframe.models import db, BaseScopedNameMixin
from eventframe.models.website import NodeMixin, Node


class FileFolder(NodeMixin, Node):
    __tablename__ = 'file_folder'


class File(BaseScopedNameMixin, db.Model):
    __tablename__ = 'file'
    file_folder_id = db.Column(None, db.ForeignKey('file_folder.id'), nullable=False)
    file_folder = db.relationship(FileFolder)
    parent = db.synonym('file_folder')
    url = db.Column(db.Unicode(250), nullable=False)

    __table_args__ = (db.UniqueConstraint('file_folder_id', 'name'))
