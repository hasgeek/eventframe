# -*- coding: utf-8 -*-

from blinker import Namespace

signals = Namespace()

signal_login = signals.signal('login')
signal_logout = signals.signal('logout')
