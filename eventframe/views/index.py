# -*- coding: utf-8 -*-

from flask import render_template
from eventframe import app, eventapp


@app.route('/')
def index():
    return render_template('index.html')


@eventapp.route('/', endpoint='index')
def event_index():
    return "index"


@eventapp.route('/<path:path>')
def page(path):
    # TODO: Look up hostname and page in known hosts. Render with appropriate template
    return "Page!"
    return render_template('page.html')
