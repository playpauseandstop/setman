from django.conf import settings


if not 'django_nose' in settings.INSTALLED_APPS or \
   not settings.TEST_RUNNER.startswith('django_nose.'):
    from testproject.core.tests.test_models import *
    from testproject.core.tests.test_settings import *
    from testproject.core.tests.test_utils import *
    from testproject.core.tests.test_version import *
