# -*- coding: utf-8 -*-

from urlparse import urljoin
from functools import wraps
from flask import g, request, url_for, redirect, session, abort
from flask_lastuser import UserInfo as LastuserInfo
from coaster.auth import add_auth_attribute, current_auth
from coaster.views import get_next_url, get_current_url
from eventframe import app, eventapp
from eventframe.signals import signal_login, signal_logout
from eventframe.models import db, LoginCode, User


def requires_scope(*scope):
    """
    Replicates functionality of lastuser.requires_scope for the event app
    """
    def inner(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_auth.is_anonymous:
                return redirect(url_for('login', next=get_current_url()))
            has_scope = set(current_auth.user.lastuser_token_scope.split(' '))
            need_scope = set(scope)
            if need_scope - has_scope != set([]):
                # Need additional scope. Send user to Lastuser for access rights
                return login(scope=' '.join(scope), next=get_current_url())
            return f(*args, **kwargs)
        return decorated_function
    return inner


@eventapp.route('/login')
def login(scope='', next=None):
    if next is None:
        next = get_next_url(external=False, referrer=True)
    code = LoginCode(next_url=next,
        return_url=url_for('login_return', _external=True), scope=scope)
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
            lookup_current_user(code.user)
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
    signal_logout.send(eventapp, user=current_auth.user)
    add_auth_attribute('user', None)
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
def lookup_current_user(user=None):
    add_auth_attribute('user', None)
    g.user = None
    add_auth_attribute('lastuserinfo', None)
    if 'userid' in session:
        if user is None:
            user = User.query.filter_by(userid=session['userid']).first()
        add_auth_attribute('user', user)
        g.user = user
        if user:
            add_auth_attribute('lastuserinfo', LastuserInfo(token=user.lastuser_token,
                token_type=user.lastuser_token_type,
                token_scope=user.lastuser_token_scope,
                userid=user.userid,
                username=user.username,
                fullname=user.fullname,
                email=user.email,
                permissions=user.userinfo.get('permissions', ()),
                organizations=user.userinfo.get('organizations')))


@eventapp.after_request
def cache_expiry_headers(response):
    if 'Expires' not in response.headers:
        response.headers['Expires'] = 'Fri, 01 Jan 1990 00:00:00 GMT'
    if 'Cache-Control' in response.headers:
        if 'private' not in response.headers['Cache-Control']:
            response.headers['Cache-Control'] = 'private, ' + response.headers['Cache-Control']
    else:
        response.headers['Cache-Control'] = 'private'
    return response
