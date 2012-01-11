from django.conf import settings


if not 'django_nose' in settings.INSTALLED_APPS or \
   not settings.TEST_RUNNER.startswith('django_nose.'):
    from testapp.tests.test_commands import *
    from testapp.tests.test_forms import *
    from testapp.tests.test_helpers import *
    from testapp.tests.test_models import *
    from testapp.tests.test_settings import *
    from testapp.tests.test_ui import *
    from testapp.tests.test_utils import *
    from testapp.tests.test_version import *
