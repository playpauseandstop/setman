from decimal import Decimal

from django.core.urlresolvers import reverse
from django.test import TestCase, Client, Approximate


from setman import settings
from setman.models import Settings
from setman.utils import AVAILABLE_SETTINGS

__all__ = ('TestUISettingsForm', )


class TestUISettingsForm(TestCase):

    def tearDown(self):
        settings._clear()

    def setUp(self):
        self.edit_settings_url = reverse('edit-settings')

    def test_edit_settings_form_default_value(self):
        c = Client()
        response = c.get(self.edit_settings_url)
        self.assertContains(response, 'Started with s')

    def test_edit_settings_form_value_from_db(self):
        settings.STRING_SETTING = 'Changed string'
        settings.save()
        c = Client()
        response = c.get(self.edit_settings_url)
        self.assertContains(response, 'Changed string')

    def test_edit_settings_form(self):
        c = Client()
        response = c.get(self.edit_settings_url)
        self.assertContains(response, 'type="checkbox"')
        self.assertContains(response,
            '<select name="CHOICE_SETTING" id="id_CHOICE_SETTING">')

        for choice in AVAILABLE_SETTINGS.CHOICE_SETTING.choices:
            if choice != AVAILABLE_SETTINGS.CHOICE_SETTING.default:
                self.assertContains(response,
                '<option value="%s">%s</option>' % (choice, choice))
            else:
                self.assertContains(response,
                '<option value="%s" selected="selected">%s</option>'
                % (choice, choice))

    def test_edit_settings_form_save(self):
        c = Client()
        response = c.post(self.edit_settings_url,
            {'STRING_SETTING': ['new_string'],
             'INT_SETTING': ['25'],
             'DECIMAL_SETTING': ['5.8'],
             'CHOICE_SETTING': ['apple'],
             'FLOAT_SETTING': ['79.4']})
        self.assertEqual(getattr(settings, 'STRING_SETTING'), 'new_string')
        self.assertEqual(getattr(settings, 'INT_SETTING'), 25)
        self.assertEqual(getattr(settings, 'BOOLEAN_SETTING'), False)
        self.assertEqual(getattr(settings, 'DECIMAL_SETTING'), Decimal('5.8'))
        self.assertEqual(getattr(settings, 'CHOICE_SETTING'), 'apple')
        self.assertEqual(getattr(settings, 'FLOAT_SETTING'), Approximate(79.4))

    def test_edit_settings_limits(self):
        c = Client()
        response = c.post(self.edit_settings_url,
            {'STRING_SETTING': ['new_string'],
             'INT_SETTING': ['36'],
             'DECIMAL_SETTING': ['15.8'],
             'CHOICE_SETTING': ['apple'],
             'FLOAT_SETTING': ['79.4']})

        # Max Value
        self.assertContains(response,
            'Ensure this value is less than or equal to 32.')
        self.assertContains(response,
            'Ensure this value is less than or equal to 10.')

        response = c.post(self.edit_settings_url,
            {'STRING_SETTING': ['new_string'],
             'INT_SETTING': ['1'],
             'DECIMAL_SETTING': ['-1.8'],
             'CHOICE_SETTING': ['apple'],
             'FLOAT_SETTING': ['79.4']})

        # Min Value
        self.assertContains(response,
            'Ensure this value is greater than or equal to 16.')
        self.assertContains(response,
            'Ensure this value is greater than or equal to 0.')

    def test_homepage(self):
        c = Client()
        response = c.get(reverse('homepage'))
        self.assertContains(response, 'Edit Settings')
        self.assertContains(response, self.edit_settings_url)
