from decimal import Decimal

from django.test import TestCase

from setman.models import Settings


__all__ = ('TestSettingsModel', )


TEST_SETTINGS = {
    'BOOLEAN_SETTING': False,
    'CHOICE_SETTING': 'pear',
    'DECIMAL_SETTING': Decimal('8.5'),
    'INT_SETTING': 24,
    'FLOAT_SETTING': 80.4,
    'STRING_SETTING': 'Started with s',
}


class TestSettingsModel(TestCase):

    def test_cache(self):
        Settings.objects.create(data=TEST_SETTINGS)

        with self.assertNumQueries(1):
            settings = Settings.objects.get()

            for key, value in TEST_SETTINGS.items():
                self.assertEqual(getattr(settings, key), value)

            settings = Settings.objects.get()

            for key, value in TEST_SETTINGS.items():
                self.assertEqual(getattr(settings, key), value)

        settings.BOOLEAN_SETTING = True
        settings.save()

        settings = Settings.objects.get()
        self.assertTrue(settings.BOOLEAN_SETTING)

    def test_save(self):
        settings = Settings()

        for key, value in TEST_SETTINGS.items():
            setattr(settings, key, value)

        settings.save()
        settings = Settings.objects.get()

        for key, value in TEST_SETTINGS.items():
            self.assertEqual(getattr(settings, key), value)

    def test_unique(self):
        Settings.objects.create()
        self.assertRaises(Exception, Settings.objects.create)
