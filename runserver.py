#!/usr/bin/env python
import sys

from werkzeug.serving import run_simple

from eventframe import app, eventapp, debug_app
from eventframe.models import db

if __name__ == '__main__':
    app.debug = True
    eventapp.debug = True
    application = debug_app
    db.create_all(app=app)

    try:
        port = int(sys.argv[1])
    except (IndexError, ValueError):
        port = 8090

    run_simple('0.0.0.0', port, application,
        use_reloader=True, use_debugger=True, use_evalex=True)
