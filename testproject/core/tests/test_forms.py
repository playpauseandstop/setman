from django import forms
from django.test import TestCase

from setman.forms import SettingsForm
from setman.utils import AVAILABLE_SETTINGS

from testproject.core.validators import abc_validator, xyz_validator


__all__ = ('TestForms', )


SETTINGS_FIELDS = {
    'BOOLEAN_SETTING': forms.BooleanField,
    'CHOICE_SETTING': forms.ChoiceField,
    'DECIMAL_SETTING': forms.DecimalField,
    'FLOAT_SETTING': forms.FloatField,
    'INT_SETTING': forms.IntegerField,
    'IP_SETTING': forms.IPAddressField,
    'STRING_SETTING': forms.RegexField,
    'VALIDATOR_SETTING': forms.CharField,
}


class TestForms(TestCase):

    def setUp(self):
        self.form = SettingsForm()

    def test_choice(self):
        field = self.form.fields['CHOICE_SETTING']
        choices = AVAILABLE_SETTINGS.CHOICE_SETTING.choices
        self.assertEqual(field.choices, [(item, item) for item in choices])
        self.assertEqual(field.label, 'Choice')

    def test_decimal(self):
        field = self.form.fields['DECIMAL_SETTING']
        self.assertEqual(field.decimal_places, 2)
        self.assertEqual(field.max_digits, 4)
        self.assertEqual(field.max_value, 10)
        self.assertEqual(field.min_value, 0)
        self.assertEqual(field.label, 'Decimal')

    def test_float(self):
        field = self.form.fields['FLOAT_SETTING']
        self.assertIsNone(field.max_value)
        self.assertIsNone(field.min_value)
        self.assertEqual(field.label, 'Float')

    def test_integer(self):
        field = self.form.fields['INT_SETTING']
        self.assertEqual(field.max_value, 32)
        self.assertEqual(field.min_value, 16)
        self.assertEqual(field.label, 'Int')

    def test_field(self):
        form = self.form
        self.assertEqual(len(form.fields), len(AVAILABLE_SETTINGS))

        for name, field in form.fields.items():
            self.assertIsInstance(field, SETTINGS_FIELDS[name])

    def test_regex(self):
        field = self.form.fields['STRING_SETTING']
        self.assertIsNone(field.max_length)
        self.assertIsNone(field.min_length)
        self.assertIsNotNone(field.regex)
        self.assertEqual(field.label, 'String')

    def test_validators(self):
        field = self.form.fields['VALIDATOR_SETTING']
        self.assertEqual(field.validators, [abc_validator, xyz_validator])
        self.assertEqual(field.label, 'Validator')
