from decimal import Decimal

from django.test import TestCase

from setman.exceptions import ValidationError
from setman.frameworks.django_setman.models import Settings


__all__ = ('TestSettingsModel', )


TEST_SETTINGS = {
    'BOOLEAN_SETTING': False,
    'CHOICE_SETTING': 'pear',
    'CHOICE_SETTING_WITH_LABELS': 'pear',
    'CHOICE_SETTING_WITH_GROUPS': 'John',
    'CHOICE_SETTING_WITH_LABELS_AND_GROUPS': 'potato',
    'CHOICE_SETTING_WITH_INTERNAL_CHOICES': 'writer',
    'CHOICE_SETTING_WITH_INTERNAL_MODEL_CHOICES': 'writer',
    'CHOICE_SETTING': 'pear',
    'DECIMAL_SETTING': Decimal('8.5'),
    'INT_SETTING': 24,
    'FLOAT_SETTING': 80.4,
    'STRING_SETTING': 'String String String',
    'testapp': {
        'app_setting': None,
        'setting_to_redefine': 0,
    },
}


class TestSettingsModel(TestCase):

    def test_cache(self):
        Settings.objects.create(data=TEST_SETTINGS)

        with self.assertNumQueries(1):
            settings = Settings.objects.get()

            for key, value in TEST_SETTINGS.items():
                if isinstance(value, Decimal):
                    value = str(value)
                self.assertEqual(getattr(settings, key), value)

            settings = Settings.objects.get()

            for key, value in TEST_SETTINGS.items():
                if isinstance(value, Decimal):
                    value = str(value)
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
        old_create_date = settings.create_date
        old_update_date = settings.update_date

        for key, value in TEST_SETTINGS.items():
            if isinstance(value, Decimal):
                value = str(value)
            self.assertEqual(getattr(settings, key), value)

        settings.save()
        self.assertEqual(settings.create_date, old_create_date)
        self.assertNotEqual(settings.update_date, old_update_date)

        settings = Settings.objects.get()
        self.assertEqual(settings.create_date, old_create_date)
        self.assertNotEqual(settings.update_date, old_update_date)

    def test_unique(self):
        Settings.objects.create()
        self.assertRaises(Exception, Settings.objects.create)

    def test_validation(self):
        instance = Settings.objects.create(data=TEST_SETTINGS.copy())
        instance.INT_SETTING = 12

        self.assertIsNone(instance.is_valid)
        instance.save()
