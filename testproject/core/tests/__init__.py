from django.conf import settings


if not 'django_nose' in settings.INSTALLED_APPS or \
   not settings.TEST_RUNNER.startswith('django_nose.'):
    from test_utils import *
