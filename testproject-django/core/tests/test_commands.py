from django.core.management import call_command
from django.test import TestCase

from setman.models import Settings

from testproject.core.tests.test_models import TEST_SETTINGS
from testproject.core.tests.test_ui import NEW_SETTINGS


__all__ = ('TestSetmanCmd', )


class TestSetmanCmd(TestCase):

    def test_empty_database(self):
        self.assertEqual(Settings.objects.count(), 0)
        call_command('setman_cmd', verbosity=0)
        self.assertEqual(Settings.objects.count(), 0)

    def test_filled_database(self):
        Settings.objects.create(data=NEW_SETTINGS)
        call_command('setman_cmd', verbosity=0)
        settings = Settings.objects.get()

        for key, value in NEW_SETTINGS.items():
            self.assertEqual(getattr(settings, key), value)

    def test_store_default_values(self):
        self.assertEqual(Settings.objects.count(), 0)
        call_command('setman_cmd', default_values=True, verbosity=0)
        self.assertEqual(Settings.objects.count(), 1)

        settings = Settings.objects.get()

        for key, value in TEST_SETTINGS.items():
            self.assertEqual(getattr(settings, key), value)

        settings.data = NEW_SETTINGS
        settings.save()

        call_command('setman_cmd', default_values=True, verbosity=0)
        settings = Settings.objects.get()

        for key, value in TEST_SETTINGS.items():
            self.assertEqual(getattr(settings, key), value)
