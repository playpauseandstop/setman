from django.conf import settings as django_settings
from django.core.exceptions import ValidationError
from django.test import TestCase

from setman import settings
from setman.models import Settings

from test_models import TEST_SETTINGS


__all__ = ('TestGlobalSettings', )


class TestGlobalSettings(TestCase):

    def tearDown(self):
        settings._clear()

    def test_empty_settings(self):
        for name in dir(django_settings):
            if not name.isupper():
                continue

            self.assertEqual(
                getattr(django_settings, name), getattr(settings, name)
            )

    def test_filled_settings(self):
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

        for name, value in TEST_SETTINGS.items():
            self.assertEqual(getattr(settings, name), value)

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
