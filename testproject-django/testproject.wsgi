import os
import sys


PROJECT_DIR = '/srv/django-setman'
VIRTUALENV_DIR = 'testproject/ve'

activate_this = \
    os.path.join(PROJECT_DIR, VIRTUALENV_DIR, 'bin', 'activate_this.py')

# activate virtualenv
execfile(activate_this, {'__file__': activate_this})

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ['PYTHON_EGG_CACHE'] = '/srv/python_eggs/'

# Need to add upper-level dir to syspath to reproduce dev Django environ
sys.path.append(PROJECT_DIR)

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
