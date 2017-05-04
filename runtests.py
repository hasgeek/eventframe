# -*- coding: iso-8859-15 -*-
import os
import nose

os.environ['ENVIRONMENT'] = os.environ['FLASK_ENV'] = "testing"
nose.main()
