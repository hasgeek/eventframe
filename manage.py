#!/usr/bin/env python

from coaster.manage import init_manager

import eventframe
import eventframe.models as models
import eventframe.forms as forms
import eventframe.views as views
from eventframe.models import db
from eventframe import app, init_for


if __name__ == '__main__':
    db.init_app(app)
    manager = init_manager(app, db, init_for, eventframe=eventframe, models=models, forms=forms, views=views)
    manager.run()
