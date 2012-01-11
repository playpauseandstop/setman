from django.core.management import call_command
from django.test import TestCase

from setman.frameworks.django_setman.models import Settings

from testapp.tests.test_models import TEST_SETTINGS
from testapp.tests.test_ui import NEW_SETTINGS


__all__ = ('TestSetmanCmd', )


class TestSetmanCmd(TestCase):

    def check_settings(self, settings, data):
        for key, value in data.items():
            if isinstance(value, dict):
                self.assertEqual(getattr(settings, key), value)
            else:
                self.assertEqual(str(getattr(settings, key)), str(value))

    def test_empty_database(self):
        self.assertEqual(Settings.objects.count(), 0)
        call_command('setman_cmd', verbosity=0)
        self.assertEqual(Settings.objects.count(), 0)

    def test_filled_database(self):
        Settings.objects.create(data=NEW_SETTINGS)
        call_command('setman_cmd', verbosity=0)
        settings = Settings.objects.get()
        self.check_settings(settings, NEW_SETTINGS)

    def test_store_default_values(self):
        self.assertEqual(Settings.objects.count(), 0)
        call_command('setman_cmd', default_values=True, verbosity=0)
        self.assertEqual(Settings.objects.count(), 1)

        settings = Settings.objects.get()
        self.check_settings(settings, TEST_SETTINGS)

        settings.data = NEW_SETTINGS
        settings.save()

        call_command('setman_cmd', default_values=True, verbosity=0)

        settings = Settings.objects.get()
        self.check_settings(settings, TEST_SETTINGS)
