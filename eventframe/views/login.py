# -*- coding: utf-8 -*-

from flask import g, request, Response, redirect, flash, abort
from flask.ext.lastuser import LastUser
from flask.ext.lastuser.sqlalchemy import UserManager
from coaster.views import get_next_url

from eventframe import app
from eventframe.models import db, User, LoginCode

lastuser = LastUser(app)
lastuser.init_usermanager(UserManager(db, User))


@app.route('/login/event')
@lastuser.requires_login
def login_event():
    if 'code' in request.args:
        code = LoginCode.query.filter_by(code=request.args['code']).first()
        if code and not code.user:
            code.user = g.user
            db.session.commit()
            # Redirect to event website
            return redirect(code.return_url + '?code=' + code.code, code=302)
        else:
            abort(403)


@app.route('/login')
@lastuser.login_handler
def login():
    return {'scope': 'id'}


@app.route('/logout')
@lastuser.logout_handler
def logout():
    flash(u"You are now logged out", category='success')
    return get_next_url()


@app.route('/login/redirect')
@lastuser.auth_handler
def lastuserauth():
    # Save the user object
    db.session.commit()
    return redirect(get_next_url())


@lastuser.auth_error_handler
def lastuser_error(error, error_description=None, error_uri=None):
    if error == 'access_denied':
        flash("You denied the request to login", category='error')
        return redirect(get_next_url())
    return Response(u"Error: %s\n"
                    u"Description: %s\n"
                    u"URI: %s" % (error, error_description, error_uri),
                    mimetype="text/plain")
