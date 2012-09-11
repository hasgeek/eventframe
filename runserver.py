#!/usr/bin/env python
from werkzeug.serving import run_simple

from eventframe import app, eventapp, init_for
from eventframe.models import db

app.debug = True
eventapp.debug = True
application = init_for('development')
db.create_all(app=app)

run_simple('0.0.0.0', 8090, application,
    use_reloader=True, use_debugger=True, use_evalex=True)
