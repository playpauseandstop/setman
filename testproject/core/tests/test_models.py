from decimal import Decimal

from django.test import TestCase

from setman.models import Settings


__all__ = ('TestSettings', )


TEST_SETTINGS = {
    'BOOLEAN_SETTING': False,
    'CHOICE_SETTING': 'pear',
    'DECIMAL_SETTING': Decimal('8.5'),
    'INT_SETTING': 24,
    'FLOAT_SETTING': 80.4,
    'STRING_SETTING': 'Started with s',
}


class TestSettings(TestCase):

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
