import os

from decimal import Decimal

from django.conf import settings as django_settings
from django.test import TestCase

from setman.frameworks.django_setman import Framework as DjangoFramework
from setman.utils.parsing import parse_config, parse_configs

from testapp.validators import abc_validator, test_runner_validator, \
    xyz_validator


__all__ = ('TestUtils', )


class TestUtils(TestCase):

    def setUp(self):
        self.framework = DjangoFramework()

    def test_parse_config_path(self):
        def check(path, relative_path=False):
            settings = parse_config(path)
            self.assertEqual(len(settings), 0 if relative_path else 1)

            if relative_path:
                return

            self.assertEqual(
                settings.TEST_RUNNER.default, 'django.test.simple.TestRunner'
            )
            self.assertEqual(settings.TEST_RUNNER.type, 'string')
            self.assertEqual(
                settings.TEST_RUNNER.validators, [test_runner_validator]
            )

        check('test_settings.cfg', True)
        check(os.path.join(django_settings.DIRNAME, 'test_settings.cfg'))

    def test_parse_configs_default_path(self):
        settings = parse_configs(self.framework)

        self.assertEqual(len(settings), 14)
        self.assertEqual(settings.path,
                         os.path.join(django_settings.DIRNAME, 'settings.cfg'))

        setting = settings.BOOLEAN_SETTING
        self.assertEqual(setting.default, False)
        self.assertIsNotNone(setting.label)
        self.assertIsNotNone(setting.help_text)

        setting = settings.CHOICE_SETTING
        self.assertEqual(setting.default, 'pear')
        self.assertEqual(
            setting.choices,
            (('apple', 'apple'), ('grape', 'grape'), ('peach', 'peach'),
             ('pear', 'pear'), ('waterlemon', 'waterlemon'))
        )
        self.assertIsNotNone(setting.label)
        self.assertIsNotNone(setting.help_text)

        setting = settings.DECIMAL_SETTING
        self.assertEqual(setting.default, Decimal('8.5'))
        self.assertEqual(setting.max_digits, 4)
        self.assertEqual(setting.decimal_places, 2)
        self.assertEqual(setting.min_value, Decimal('0'))
        self.assertEqual(setting.max_value, Decimal('10'))
        self.assertIsNotNone(setting.label)
        self.assertIsNotNone(setting.help_text)

        setting = settings.INT_SETTING
        self.assertEqual(setting.default, 24)
        self.assertEqual(setting.min_value, 16)
        self.assertEqual(setting.max_value, 32)
        self.assertIsNotNone(setting.label)
        self.assertIsNotNone(setting.help_text)

        setting = settings.FLOAT_SETTING
        self.assertEqual(setting.default, 80.4)
        self.assertIsNotNone(setting.label)
        self.assertIsNotNone(setting.help_text)
        self.assertFalse(
            hasattr(setting, 'wrong_arg'), '%r has wrong_arg attr' % setting
        )

        setting = settings.STRING_SETTING
        self.assertEqual(setting.default, 'String String String')
        self.assertTrue(
            hasattr(setting, 'regex'), '%r has not regex attr' % setting
        )
        self.assertIsNotNone(setting.regex)
        self.assertIsNotNone(setting.label)
        self.assertIsNotNone(setting.help_text)

    def test_parse_configs_additional_type(self):
        settings = parse_configs(self.framework)

        setting = settings.IP_SETTING
        self.assertEqual(setting.type, 'ip')
        self.assertEqual(setting.default, '127.0.0.1')

    def test_parse_configs_validators(self):
        settings = parse_configs(self.framework)

        setting = settings.BOOLEAN_SETTING
        self.assertEqual(setting.validators, [])

        setting = settings.VALIDATOR_SETTING
        self.assertIn(abc_validator, setting.validators)
        self.assertIn(xyz_validator, setting.validators)
        self.assertEqual(setting.validators, [abc_validator, xyz_validator])
