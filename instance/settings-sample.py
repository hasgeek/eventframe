# -*- coding: utf-8 -*-
#: Debug mode (put this value in development.py only, never in settings.py)
DEBUG = True
#: Site title
SITE_TITLE = 'HasGeek Eventframe'
#: Site id (for network bar)
SITE_ID = 'events'
#: Admin domains. The first is considered primary
ADMIN_HOSTS = ['eventframe.hasgeek.com', 'efdev.hasgeek.in']
#: Login host for event apps. This is the admin host and optional port number
LOGIN_HOST = 'eventframe.hasgeek.com:443'
#: Using SSL?
USE_SSL = True
#: Database backend
SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
#: Secret key
SECRET_KEY = 'make this something random'
#: Timezone
TIMEZONE = 'Asia/Calcutta'
#: LastUser server
LASTUSER_SERVER = 'https://auth.hasgeek.com/'
#: LastUser client id
LASTUSER_CLIENT_ID = ''
#: LastUser client secret
LASTUSER_CLIENT_SECRET = ''
#: Path to site themes (must be an absolute path)
THEME_PATHS = ''
#: Mail settings
#: MAIL_FAIL_SILENTLY : default True
#: MAIL_SERVER : default 'localhost'
#: MAIL_PORT : default 25
#: MAIL_USE_TLS : default False
#: MAIL_USE_SSL : default False
#: MAIL_USERNAME : default None
#: MAIL_PASSWORD : default None
#: DEFAULT_MAIL_SENDER : default None
MAIL_FAIL_SILENTLY = False
MAIL_SERVER = 'localhost'
DEFAULT_MAIL_SENDER = ('HasGeek', 'test@example.com')
#: Logging: recipients of error emails
ADMINS = []
#: Log file
LOGFILE = 'error.log'
