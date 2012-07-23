# -*- coding: utf-8 -*-

from urlparse import urljoin

from flask import g, request, url_for, redirect, session, abort
from coaster.views import get_next_url
from eventframe import app, eventapp
from eventframe.signals import signal_login, signal_logout
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
            g.user = code.user
            signal_login.send(eventapp, user=code.user)
            db.session.delete(code)
            db.session.commit()
            return redirect(code.next_url or url_for('index'))
        elif code:
            db.session.delete(code)
            db.session.commit()
    abort(403)


@eventapp.route('/logout')
def logout():
    code = LoginCode(next_url=get_next_url(external=False, referrer=True),
        return_url=url_for('logout_return', _external=True))
    session.pop('userid', None)
    signal_logout.send(eventapp, user=g.user)
    g.user = None
    db.session.add(code)
    db.session.commit()
    if app.config.get('USE_SSL'):
        scheme = 'https://'
    else:
        scheme = 'http://'
    return redirect(urljoin(scheme + app.config['LOGIN_HOST'], '/logout?code=' + code.code))


@eventapp.route('/logout/redirect')
def logout_return():
    if 'code' in request.args:
        code = LoginCode.query.filter_by(code=request.args['code']).first()
        if code:
            db.session.delete(code)
            db.session.commit()
    return redirect(get_next_url(external=False, referrer=True))


@eventapp.before_request
def lookup_current_user():
    g.user = None
    if 'userid' in session:
        g.user = User.query.filter_by(userid=session['userid']).first()
