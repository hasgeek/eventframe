# -*- coding: utf-8 -*-

import urlparse

from flask import g, request, Response, redirect, flash, abort, url_for
from coaster.views import get_next_url, get_current_url

from eventframe import app, lastuser
from eventframe.signals import signal_login, signal_logout
from eventframe.models import db, LoginCode


@app.route('/login/event')
def login_event():
    if 'code' in request.args:
        code = LoginCode.query.filter_by(code=request.args['code']).first()
        if code and not code.user:
            if not g.user:
                return login(scope=code.scope, next=get_current_url())
            # Check for scope expansion
            has_scope = set(g.user.lastuser_token_scope.split(' '))
            need_scope = set(code.scope.split(' '))
            if '' in need_scope:
                need_scope.remove('')
            if need_scope - has_scope != set([]):
                # Need additional scope. Send user to Lastuser for access rights
                return login(scope=code.scope, next=get_current_url())
            code.user = g.user
            db.session.commit()
            # Redirect to event website
            if urlparse.urlsplit(code.return_url).query:
                return redirect(code.return_url + '&code=' + code.code, code=302)
            else:
                return redirect(code.return_url + '?code=' + code.code, code=302)
        elif code:
            db.session.delete(code)
            db.session.commit()
    abort(403)


@app.route('/login')
@lastuser.login_handler
def login(scope=None, next=None):
    basescope = 'id email'
    if scope:
        basescope = ' '.join(set(basescope.split(' ')) | set(scope.split(' ')))

    return {'scope': basescope, 'next': next}


@app.route('/logout/event')
def logout_event():
    if 'code' in request.args:
        code = LoginCode.query.filter_by(code=request.args['code']).first()
        if code:
            # Redirect to event website
            if urlparse.urlsplit(code.return_url).query:
                return redirect(code.return_url + '&code=' + code.code, code=302)
            else:
                return redirect(code.return_url + '?code=' + code.code, code=302)
        else:
            return url_for('index')


@app.route('/logout')
@lastuser.logout_handler
def logout():
    code = None
    if 'code' in request.args:
        code = LoginCode.query.filter_by(code=request.args['code']).first()
    if code:
        next = url_for('logout_event', code=code.code)
    else:
        next = get_next_url()
        flash(u"You are now logged out", category='success')
    signal_logout.send(app, user=g.user)
    return next


@app.route('/login/redirect')
@lastuser.auth_handler
def lastuserauth():
    # Save the user object
    signal_login.send(app, user=g.user)
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
