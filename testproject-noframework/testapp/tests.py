import os
import unittest

from decimal import Decimal

from setman import settings
from setman.exceptions import ValidationError
from setman.utils.parsing import is_settings_container
from setman.utils.types import BooleanSetting, DecimalSetting, IntSetting, \
    StringSetting

from testapp.app import configure_settings


class TestIni(unittest.TestCase):

    format = 'ini'

    def setUp(self):
        configure_settings(self.format)
        self.filename = settings._backend.filename

    def tearDown(self):
        settings._backend = None
        settings._framework = None

        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def test_available_settings(self):
        self.assertEqual(len(settings.available_settings), 4)

        setting = settings.available_settings.max_processes
        self.assertEqual(setting.default, 2)
        self.assertIsInstance(setting, IntSetting)

        setting = settings.available_settings.hosts_file
        self.assertEqual(setting.default, '/etc/hosts')
        self.assertIsInstance(setting, StringSetting)

        setting = settings.available_settings.hourly_rate
        self.assertEqual(setting.default, Decimal(15))
        self.assertIsInstance(setting, DecimalSetting)

        container = settings.available_settings.testapp
        self.assertTrue(is_settings_container(container))

        setting = settings.available_settings.testapp.debug
        self.assertEqual(setting.default, False)
        self.assertIsInstance(setting, BooleanSetting)

    def test_convert_value(self):
        settings.max_processes = '16'
        settings.save()

        self.assertEqual(settings.max_processes, 16)

        settings.max_processes = 'abc'
        self.assertFalse(settings.is_valid())

    def test_defaults(self):
        self.assertEqual(settings.max_processes, 2)
        self.assertEqual(settings.hosts_file, '/etc/hosts')
        self.assertEqual(settings.hourly_rate, Decimal(15))
        self.assertFalse(settings.testapp.debug)

    def test_restore(self):
        settings.max_processes = 4
        settings.hosts_file = '/etc/hosts.new'
        settings.hourly_rate = Decimal(10)
        settings.testapp.debug = True
        settings.save()

        settings.revert()
        self.assertEqual(settings.max_processes, 2)
        self.assertEqual(settings.hosts_file, '/etc/hosts')
        self.assertEqual(settings.hourly_rate, Decimal(15))
        self.assertFalse(settings.testapp.debug)

    def test_validators(self):
        settings.max_processes = 24
        self.assertFalse(settings.is_valid())
        self.assertRaises(ValueError, settings.save)

        settings.max_processes = 4
        settings.hosts_file = 'something'
        self.assertFalse(settings.is_valid())
        self.assertRaises(ValueError, settings.save)

        settings.max_processes = 4
        settings.hosts_file = '/etc/hosts.new'
        settings.hourly_rate = Decimal('0.5')
        self.assertFalse(settings.is_valid())
        self.assertRaises(ValueError, settings.save)

        settings.hourly_rate = Decimal('12.725')
        self.assertFalse(settings.is_valid())
        self.assertRaises(ValueError, settings.save)

        settings.hourly_rate = Decimal('1200.50')
        self.assertFalse(settings.is_valid())
        self.assertRaises(ValueError, settings.save)

        settings.hourly_rate = Decimal('10.00')
        self.assertTrue(settings.is_valid())
        settings.save()

    def test_workflow(self):
        settings.max_processes = 4
        settings.hosts_file = '/etc/hosts.new'
        settings.hourly_rate = Decimal(10)
        settings.testapp.debug = True
        settings.save()

        self.assertTrue(os.path.isfile(self.filename))

        handler = open(self.filename, 'r')
        content = handler.read()
        handler.close()

        if self.format == 'ini':
            self.assertIn('max_processes = 4', content)
            self.assertIn('hosts_file = /etc/hosts.new', content)
            self.assertIn('hourly_rate = 10', content)
            self.assertIn('[testapp]', content)
            self.assertIn('debug = True', content)
        elif self.format == 'json':
            self.assertIn('"max_processes": 4', content)
            self.assertIn('"hosts_file": "/etc/hosts.new"', content)
            self.assertIn('"hourly_rate": "10"', content)
            self.assertIn('"testapp": {"debug": true}', content)

        # Re-check backend data
        self.assertEqual(settings.max_processes, 4)
        self.assertEqual(settings.hosts_file, '/etc/hosts.new')
        self.assertEqual(settings.hourly_rate, Decimal(10))
        self.assertTrue(settings.testapp.debug)


class TestJson(TestIni):

    format = 'json'


class TestPickle(TestIni):

    format = 'pickle'


if __name__ == '__main__':
    unittest.main()
