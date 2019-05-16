# -*- coding: utf-8 -*-

from flask import render_template
from eventframe import app
from eventframe.models.website import Website
from eventframe.views.login import lastuser


@app.route('/')
def index():
    websites = Website.query.order_by(Website.title).all()
    return render_template('index.html.jinja2', websites=websites, admin=lastuser.has_permission('siteadmin'))
