from django import forms
from django.test import TestCase

from setman.forms import SettingsForm
from setman.utils import AVAILABLE_SETTINGS

from testproject.core.choices import ROLE_CHOICES
from testproject.core.validators import abc_validator, xyz_validator


__all__ = ('TestForms', )


SETTINGS_FIELDS = {
    'BOOLEAN_SETTING': forms.BooleanField,
    'CHOICE_SETTING': forms.ChoiceField,
    'core.app_setting': forms.CharField,
    'core.setting_to_redefine': forms.IntegerField,
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
        self.assertEqual(
            field.choices,
            [('apple', 'apple'), ('grape', 'grape'), ('peach', 'peach'),
             ('pear', 'pear'), ('waterlemon', 'waterlemon')]
        )
        self.assertEqual(field.label, 'Choice')

        field = self.form.fields['CHOICE_SETTING_WITH_LABELS']
        self.assertEqual(
            field.choices,
            [('apple', 'Apple'), ('grape', 'Grape'), ('peach', 'Peach'),
             ('pear', 'Pear'), ('waterlemon', 'Waterlemon')]
        )
        self.assertEqual(field.label, 'Choice with labels')

        field = self.form.fields['CHOICE_SETTING_WITH_GROUPS']
        self.assertEqual(
            field.choices,
            [
                ('Male', (
                    ('Henry', 'Henry'),
                    ('John', 'John'),
                    ('Peter', 'Peter'),
                )),
                ('Female', (
                    ('Henrietta', 'Henrietta'),
                    ('Johanna', 'Johanna'),
                    ('Kate', 'Kate')
                )),
            ]
        )
        self.assertEqual(field.label, 'Choice with groups')

        field = self.form.fields['CHOICE_SETTING_WITH_LABELS_AND_GROUPS']
        self.assertEqual(
            field.choices,
            [
                ('Fruits', (
                    ('apple', 'Apple'),
                    ('grape', 'Grape'),
                    ('peach', 'Peach'),
                    ('pear', 'Pear')
                )),
                ('Vegetables', (
                    ('carrot', 'Carrot'),
                    ('cucumber', 'Cucumber'),
                    ('potato', 'Potato'),
                    ('tomato', 'Tomato'),
                )),
            ]
        )
        self.assertEqual(field.label, 'Choice with labels and groups')

        field = self.form.fields['CHOICE_SETTING_WITH_INTERNAL_CHOICES']
        self.assertEqual(field.choices, list(ROLE_CHOICES))
        self.assertEqual(field.label, 'Choice with internal choices')

        field = \
            self.form.fields['CHOICE_SETTING_WITH_INTERNAL_MODEL_CHOICES_1']
        self.assertEqual(field.choices, list(ROLE_CHOICES))
        self.assertEqual(field.label, 'Choice with internal model choices')

        field = \
            self.form.fields['CHOICE_SETTING_WITH_INTERNAL_MODEL_CHOICES_2']
        self.assertEqual(field.choices, list(ROLE_CHOICES))
        self.assertEqual(field.label, 'Choice with internal model choices')

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
        settings_counter = len(AVAILABLE_SETTINGS) - 1 + \
                           len(AVAILABLE_SETTINGS.core)
        self.assertEqual(len(form.fields), settings_counter)

        for name, field in form.fields.items():
            if not name in SETTINGS_FIELDS and name.startswith('CHOICE_'):
                result = forms.ChoiceField
            else:
                result = SETTINGS_FIELDS[name]
            self.assertIsInstance(field, result)

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
