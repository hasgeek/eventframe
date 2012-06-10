#!/usr/bin/env python
from werkzeug.serving import run_simple

import os
os.environ['ENVIRONMENT'] = "development"
from eventframe import app, eventapp, application
from eventframe.models import db

app.debug = True
eventapp.debug = True

db.create_all(app=app)

run_simple('0.0.0.0', 8090, application,
    use_reloader=True, use_debugger=True, use_evalex=True)
