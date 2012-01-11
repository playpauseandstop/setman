import copy
import os
import sys
import unittest

from decimal import Decimal

from flask import url_for
from setman import settings

from testapp import app


DEFAULT_SETTINGS = {
    'BOOLEAN_SETTING': False,
    'CHOICE_SETTING': 'pear',
    'CHOICE_SETTING_WITH_LABELS': 'pear',
    'CHOICE_SETTING_WITH_GROUPS': 'John',
    'CHOICE_SETTING_WITH_LABELS_AND_GROUPS': 'potato',
    'CHOICE_SETTING_WITH_INTERNAL_CHOICES': 'writer',
    'CHOICE_SETTING': 'pear',
    'DECIMAL_SETTING': Decimal('8.5'),
    'IP_SETTING': '127.0.0.1',
    'INT_SETTING': 24,
    'FLOAT_SETTING': 80.4,
    'STRING_SETTING': 'Started with s',
    'testapp': {
        'app_setting': None,
        'setting_to_redefine': 0,
    },
    'VALIDATOR_SETTING': None,
}

NEW_SETTINGS = {
    'BOOLEAN_SETTING': True,
    'CHOICE_SETTING': 'waterlemon',
    'CHOICE_SETTING_WITH_LABELS': 'waterlemon',
    'CHOICE_SETTING_WITH_GROUPS': 'Kate',
    'CHOICE_SETTING_WITH_LABELS_AND_GROUPS': 'grape',
    'CHOICE_SETTING_WITH_INTERNAL_CHOICES': 'editor',
    'DECIMAL_SETTING': Decimal('5.33'),
    'INT_SETTING': 20,
    'IP_SETTING': '192.168.1.2',
    'FLOAT_SETTING': 189.2,
    'STRING_SETTING': 'setting',
    'testapp': {
        'app_setting': 'someone',
        'setting_to_redefine': 24,
    },
    'VALIDATOR_SETTING': 'abc xyz',
}

WRONG_SETTINGS = {
    'CHOICE_SETTING': ('pepper', ),
    'CHOICE_SETTING_WITH_LABELS': ('pepper', ),
    'CHOICE_SETTING_WITH_GROUPS': ('Michael', ),
    'CHOICE_SETTING_WITH_LABELS_AND_GROUPS': ('pepper', ),
    'CHOICE_SETTING_WITH_INTERNAL_CHOICES': ('admin', ),
    'DECIMAL_SETTING': (Decimal(-1), Decimal(12), Decimal('8.3451')),
    'INT_SETTING': (12, 48),
    'IP_SETTING': ('127.0.0', ),
    'FLOAT_SETTING': ('', ),
    'STRING_SETTING': ('Not started from s', ),
    'testapp': {
        'app_setting': ('something', ),
        'setting_to_redefine': (72, ),
    },
    'VALIDATOR_SETTING': ('abc', 'xyz', 'Something'),
}


class TestCase(unittest.TestCase):

    def setUp(self):
        self.old_backend_filename = settings._backend.filename
        settings._backend.filename += '.test'

        self.app = app.test_client()
        self.edit_url = self.url('setman.edit')
        self.revert_url = self.url('setman.revert')

    def tearDown(self):
        backend_filename = settings._backend.filename

        settings._backend.filename = self.old_backend_filename
        settings._backend.clear()

        if os.path.isfile(backend_filename):
            os.unlink(backend_filename)

    def url(self, *args, **kwargs):
        with app.test_request_context():
            return url_for(*args, **kwargs)


class TestSetmanBlueprint(TestCase):

    def check_settings(self, data, prefix=None):
        values = getattr(settings, prefix) if prefix else settings

        for name, value in data.iteritems():
            if isinstance(value, dict):
                self.check_settings(value, name)
            else:
                from_values = getattr(values, name)

                if name in ('app_setting', 'VALIDATOR_SETTING') and not value:
                    self.assertIn(from_values, ('', None))
                else:
                    self.assertEqual(from_values, value)

    def prepare_data(self, data, prefix=None):
        results = {}

        for name, value in data.iteritems():
            if isinstance(value, dict):
                results.update(self.prepare_data(value, name))
            else:
                name = '%s__%s' % (prefix, name) if prefix else name

                if name == 'BOOLEAN_SETTING':
                    if not value:
                        continue
                    value = 'y'

                results.update({name: value})

        return results

    def save_settings(self, data, prefix=None):
        values = getattr(settings, prefix) if prefix else settings

        for name, value in data.iteritems():
            if isinstance(value, dict):
                self.save_settings(value, name)
            else:
                setattr(values, name, value)

        values.save()

    def test_edit(self):
        response = self.app.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Edit Settings', response.data)
        self.assertIn('testapp settings</h2>', response.data)
        self.assertIn('Project settings</h2>', response.data)

        data = self.prepare_data(NEW_SETTINGS)
        response = self.app.post(self.edit_url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.edit_url, dict(response.header_list)['Location'])

        self.check_settings(NEW_SETTINGS)

        data = self.prepare_data(DEFAULT_SETTINGS)
        response = self.app.post(self.edit_url,
                                 data=data,
                                 follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Edit Settings', response.data)
        self.assertIn('Settings have been succesfully updated.', response.data)
        self.assertNotIn('Settings cannot be saved cause of validation ' \
                         'issues. Check for errors below.', response.data)

        self.check_settings(DEFAULT_SETTINGS)

    def test_edit_errors(self):
        pass

    def test_revert(self):
        self.check_settings(DEFAULT_SETTINGS)
        self.save_settings(NEW_SETTINGS)

        response = self.app.get(self.edit_url)
        self.check_settings(NEW_SETTINGS)

        response = self.app.get(self.revert_url, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Edit Settings', response.data)
        self.assertIn('Settings have been reverted to default values.',
                      response.data)

        self.check_settings(DEFAULT_SETTINGS)


class TestTestapp(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main(failfast='--failfast' in sys.argv)
