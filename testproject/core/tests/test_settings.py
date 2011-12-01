from django.conf import settings as django_settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase

from setman import settings
from setman.models import Settings
from setman.utils import is_settings_container

from testproject.core.tests.test_models import TEST_SETTINGS


__all__ = ('TestGlobalSettings', )


class TestGlobalSettings(TestCase):

    def setUp(self):
        settings._clear()
        cache.clear()

    def tearDown(self):
        self.setUp()

    def test_app_settings(self):
        self.assertRaises(AttributeError, getattr, settings, 'auth')

        self.assertTrue(hasattr(settings, 'core'))
        self.assertTrue(is_settings_container(settings.core))
        self.assertEqual(settings.core.app_setting, None)
        self.assertEqual(settings.core.setting_to_redefine, 0)

        settings.core.app_setting = 'string'
        settings.core.setting_to_redefine = 60
        settings.save()

        settings._clear()
        cache.clear()

        self.assertEqual(settings.core.app_setting, 'string')
        self.assertEqual(settings.core.setting_to_redefine, 60)

    def test_default_values(self, prefix=None):
        data = TEST_SETTINGS[prefix] if prefix else TEST_SETTINGS
        values = getattr(settings, prefix) if prefix else settings

        self.assertEqual(Settings.objects.count(), 1 if prefix else 0)

        for name, value in data.items():
            self.assertTrue(hasattr(values, name))
            mixed = getattr(values, name)

            if is_settings_container(mixed):
                self.test_default_values(name)
            else:
                self.assertEqual(mixed, value)

    def test_empty_settings(self):
        for name in dir(django_settings):
            if not name.isupper():
                continue

            self.assertEqual(
                getattr(django_settings, name), getattr(settings, name)
            )

    def test_filled_settings(self):
        def check_values(prefix=None):
            data = TEST_SETTINGS[prefix] if prefix else TEST_SETTINGS
            values = getattr(settings, prefix) if prefix else settings

            for name, value in data.items():
                mixed = getattr(values, name)

                if is_settings_container(mixed):
                    check_values(name)
                else:
                    self.assertEqual(mixed, value)

        self.assertEqual(Settings.objects.count(), 0)

        instance = Settings.objects.create(data=TEST_SETTINGS)
        self.assertEqual(instance.data, TEST_SETTINGS)

        for name, value in TEST_SETTINGS.items():
            self.assertEqual(getattr(instance, name), value)

        for name in dir(django_settings):
            if not name.isupper():
                continue

            self.assertEqual(
                getattr(django_settings, name), getattr(settings, name)
            )

        check_values()

    def test_save_settings(self):
        instance = Settings.objects.create(data=TEST_SETTINGS)

        settings.BOOLEAN_SETTING = True
        settings.save()

        self.assertTrue(settings.BOOLEAN_SETTING)

        instance = Settings.objects.get()
        self.assertTrue(instance.BOOLEAN_SETTING)

        instance.BOOLEAN_SETTING = False
        instance.save()

        self.assertFalse(instance.BOOLEAN_SETTING)

    def test_validation(self):
        settings.INT_SETTING = 12
        self.assertRaises(ValidationError, settings.save)
