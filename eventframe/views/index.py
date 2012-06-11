# -*- coding: utf-8 -*-

from flask import render_template
from eventframe import app, eventapp


@app.route('/')
def index():
    return render_template('index.html')
