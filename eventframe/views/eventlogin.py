# -*- coding: utf-8 -*-

from urlparse import urljoin

from flask import g, request, url_for, redirect, session, abort
from coaster.views import get_next_url
from eventframe import app, eventapp
from eventframe.models import db, LoginCode, User


@eventapp.route('/login')
def login():
    code = LoginCode(next_url=get_next_url(external=False, referrer=True),
        return_url=url_for('login_return', _external=True))
    db.session.add(code)
    db.session.commit()
    if app.config.get('USE_SSL'):
        scheme = 'https://'
    else:
        scheme = 'http://'
    return redirect(urljoin(scheme + app.config['LOGIN_HOST'], '/login/event?code=' + code.code))


@eventapp.route('/login/redirect')
def login_return():
    if 'code' in request.args:
        code = LoginCode.query.filter_by(code=request.args['code']).first()
        if code and code.user:
            session['userid'] = code.user.userid
            db.session.delete(code)
            db.session.commit()
            return redirect(code.next_url or url_for('index'))
        elif code:
            db.session.delete(code)
            db.session.commit()
    abort(403)


@eventapp.route('/logout')
def logout():
    session.pop('userid', None)
    g.user = None
    return redirect(get_next_url(external=False, referrer=True))


@eventapp.before_request
def lookup_current_user():
    g.user = None
    if 'userid' in session:
        g.user = User.query.filter_by(userid=session['userid']).first()
