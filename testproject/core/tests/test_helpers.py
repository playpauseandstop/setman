from django.conf import settings as django_settings
from django.test import TestCase

from setman.helpers import get_config
from setman.models import Settings

from testproject.core.tests.test_models import TEST_SETTINGS


__all__ = ('TestHelpers', )


class TestHelpers(TestCase):

    def setUp(self):
        Settings.objects.create(data=TEST_SETTINGS.copy())

    def test_get_config(self):
        for key, value in TEST_SETTINGS.items():
            if key == 'core':
                continue
            self.assertEqual(get_config(key), value)

        self.assertRaises(ValueError, get_config, 'core')

        for key, value in TEST_SETTINGS['core'].items():
            self.assertEqual(get_config('core.%s' % key), value)

    def test_get_config_app_does_not_found(self):
        self.assertRaises(AttributeError, get_config, 'auth')
        self.assertRaises(AttributeError, get_config, 'auth.DOES_NOT_EXIST')
        self.assertRaises(AttributeError,
                          get_config,
                          'auth.DOES_NOT_EXIST',
                          True)

    def test_get_config_default_value(self):
        self.assertTrue(get_config('DOES_NOT_EXIST', True))
        self.assertRaises(AttributeError, get_config, 'DOES_NOT_EXIST')
        self.assertTrue(get_config('core.DOES_NOT_EXIST', True))
        self.assertRaises(AttributeError, get_config, 'core.DOES_NOT_EXIST')

    def test_get_config_django_settings(self):
        self.assertEqual(get_config('DEBUG'), django_settings.DEBUG)
        self.assertEqual(
            get_config('DEFAULT_FROM_EMAIL', 'root@localhost'),
            django_settings.DEFAULT_FROM_EMAIL
        )
