import copy

from decimal import Decimal

from django.conf import settings as django_settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase as DjangoTestCase

from setman import get_version, settings
from setman.models import Settings
from setman.utils import AVAILABLE_SETTINGS

from testproject.core.tests.test_models import TEST_SETTINGS


__all__ = ('TestAdminUI', 'TestAdminUIForbidden', 'TestUI', 'TestUIForbidden')


NEW_SETTINGS = {
    'BOOLEAN_SETTING': True,
    'CHOICE_SETTING': 'waterlemon',
    'CHOICE_SETTING_WITH_LABELS': 'waterlemon',
    'CHOICE_SETTING_WITH_GROUPS': 'Kate',
    'CHOICE_SETTING_WITH_LABELS_AND_GROUPS': 'grape',
    'CHOICE_SETTING_WITH_INTERNAL_CHOICES': 'editor',
    'CHOICE_SETTING_WITH_INTERNAL_MODEL_CHOICES_1': 'senior_editor',
    'CHOICE_SETTING_WITH_INTERNAL_MODEL_CHOICES_2': 'senior_editor',
    'DECIMAL_SETTING': Decimal('5.33'),
    'INT_SETTING': 20,
    'IP_SETTING': '192.168.1.2',
    'FLOAT_SETTING': 189.2,
    'STRING_SETTING': 'setting',
    'VALIDATOR_SETTING': 'abc xyz',
}
TEST_USERNAME = 'username'
WRONG_SETTINGS = {
    'CHOICE_SETTING': ('pepper', ),
    'CHOICE_SETTING_WITH_LABELS': ('pepper', ),
    'CHOICE_SETTING_WITH_GROUPS': ('Michael', ),
    'CHOICE_SETTING_WITH_LABELS_AND_GROUPS': ('pepper', ),
    'CHOICE_SETTING_WITH_INTERNAL_CHOICES': ('admin', ),
    'CHOICE_SETTING_WITH_INTERNAL_MODEL_CHOICES_1': ('admin', ),
    'CHOICE_SETTING_WITH_INTERNAL_MODEL_CHOICES_2': ('admin', ),
    'DECIMAL_SETTING': (Decimal(-1), Decimal(12), Decimal('8.3451')),
    'INT_SETTING': (12, 48),
    'IP_SETTING': ('127.0.0', ),
    'FLOAT_SETTING': ('', ),
    'STRING_SETTING': ('Not started from s', ),
    'VALIDATOR_SETTING': ('abc', 'xyz', 'Something'),
}


class TestCase(DjangoTestCase):

    def setUp(self):
        self.old_AUTHENTICATION_BACKENDS = \
            django_settings.AUTHENTICATION_BACKENDS
        django_settings.AUTHENTICATION_BACKENDS = (
            'django.contrib.auth.backends.ModelBackend',
        )

        self.docs_url = reverse('docs')
        self.edit_settings_url = reverse('setman_edit')
        self.home_url = reverse('home')
        self.revert_settings_url = reverse('setman_revert')
        self.view_settings_url = reverse('view_settings')

    def tearDown(self):
        django_settings.AUTHENTICATION_BACKENDS = \
            self.old_AUTHENTICATION_BACKENDS
        settings._clear()

    def login(self, username, is_admin=False):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username,
                                            password=username,
                                            email=username + '@domain.com')
        else:
            user.set_password(username)
            user.save()

        if is_admin:
            user.is_staff = True
            user.is_superuser = True
            user.save()

        client = self.client
        client.login(username=username, password=username)

        return client


class TestAdminUI(TestCase):

    def setUp(self):
        super(TestAdminUI, self).setUp()
        self.add_url = reverse('admin:setman_settings_add')
        self.admin_url = reverse('admin:index')
        self.edit_url = reverse('admin:setman_settings_changelist')

    def test_admin(self):
        relative = lambda url: url.replace(self.admin_url, '')

        response = self.client.get(self.admin_url)
        self.assertNotContains(response, 'Settings Manager')
        self.assertNotContains(response, 'Settings</a>')

        client = self.login(TEST_USERNAME, is_admin=True)
        response = client.get(self.admin_url)

        self.assertContains(response, 'Settings Manager')
        self.assertContains(
            response, '<a href="%s">Settings</a>' % relative(self.edit_url)
        )
        self.assertNotContains(
            response, '<a href="%s" class="addlink">Add</a>' % \
            relative(self.add_url)
        )
        self.assertContains(
            response,
            '<a href="%s" class="changelink">Change</a>' % \
            relative(self.edit_url)
        )

    def test_admin_edit(self):
        client = self.login(TEST_USERNAME, is_admin=True)
        response = client.get(self.edit_url)

        for setting in AVAILABLE_SETTINGS:
            self.assertContains(response, setting.label)
            self.assertContains(response, setting.help_text)

        response = client.post(self.edit_url, NEW_SETTINGS)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.edit_url, response['Location'])

        settings._clear()

        for key, value in NEW_SETTINGS.items():
            self.assertEqual(getattr(settings, key), value)


class TestAdminUIForbidden(TestCase):

    def setUp(self):
        super(TestAdminUIForbidden, self).setUp()
        self.admin_url = reverse('admin:index')
        self.old_SETMAN_AUTH_PERMITTED = settings.SETMAN_AUTH_PERMITTED
        django_settings.SETMAN_AUTH_PERMITTED = lambda user: False

    def tearDown(self):
        django_settings.SETMAN_AUTH_PERMITTED = self.old_SETMAN_AUTH_PERMITTED

    def test_admin(self):
        client = self.login(TEST_USERNAME, is_admin=True)
        response = client.get(self.admin_url)
        self.assertNotContains(response, 'Settings Manager')
        self.assertNotContains(response, 'Settings</a>')


class TestUI(TestCase):

    def test_docs(self):
        client = self.login(TEST_USERNAME)
        response = client.get(self.docs_url, follow=True)

        try:
            self.assertContains(response, 'Documentation', count=2)
        except AssertionError:
            self.assertContains(
                response,
                'django-setman %s documentation' % get_version(),
                count=4
            )

    def test_edit_settings(self):
        client = self.login(TEST_USERNAME)
        response = client.get(self.edit_settings_url)

        self.assertContains(response, 'Edit Settings', count=2)

        for setting in AVAILABLE_SETTINGS:
            self.assertContains(response, setting.label)
            self.assertContains(response, setting.help_text)

        response = client.post(self.edit_settings_url, NEW_SETTINGS)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.edit_settings_url, response['Location'])

        settings._clear()

        for key, value in NEW_SETTINGS.items():
            self.assertEqual(getattr(settings, key), value)

    def test_edit_settings_errors(self):
        client = self.login(TEST_USERNAME)

        for key, values in WRONG_SETTINGS.items():
            old_value = getattr(settings, key)

            for value in values:
                data = copy.deepcopy(TEST_SETTINGS)
                data.update({key: value})

                response = client.post(self.edit_settings_url, data)
                self.assertContains(
                    response,
                    'Settings cannot be saved cause of validation issues. ' \
                    'Check for errors below.'
                )
                self.assertContains(response, '<dd class="errors">')

                settings._clear()
                self.assertEqual(getattr(settings, key), old_value)

    def test_home(self):
        client = self.login(TEST_USERNAME)
        response = client.get(self.home_url)

        self.assertContains(
            response,
            '<li><a href="%s">Edit test project settings</a></li>' % \
            self.edit_settings_url
        )
        self.assertContains(
            response,
            '<li><a href="%s">View configuration definition and default ' \
            'values files</a></li>' % self.view_settings_url
        )

    def test_home_not_authenticated(self):
        response = self.client.get(self.home_url, follow=True)
        self.assertContains(
            response,
            'Log in with oDesk account <a href="%s?next=/">here</a>.' % \
            reverse('django_odesk.auth.views.authenticate')
        )

    def test_revert_settings(self):
        Settings.objects.create(data=NEW_SETTINGS)

        client = self.login(TEST_USERNAME)
        response = client.get(self.revert_settings_url)

        self.assertEquals(response.status_code, 302)
        self.assertIn(self.edit_settings_url, response['Location'])

        for key, value in TEST_SETTINGS.items():
            self.assertEqual(getattr(settings, key), value)

    def test_view_settings(self):
        client = self.login(TEST_USERNAME)
        response = client.get(self.view_settings_url)
        self.assertContains(
            response, 'Configuration Definition and Default Values Files',
            count=2
        )
        self.assertContains(
            response, 'Configuration Definition File', count=1
        )
        self.assertContains(response, 'Default Values File', count=3)


class TestUIForbidden(TestCase):

    def setUp(self):
        super(TestUIForbidden, self).setUp()

        self.old_SETMAN_AUTH_PERMITTED = settings.SETMAN_AUTH_PERMITTED
        django_settings.SETMAN_AUTH_PERMITTED = lambda user: user.is_superuser

    def tearDown(self):
        django_settings.SETMAN_AUTH_PERMITTED = self.old_SETMAN_AUTH_PERMITTED

    def test_edit_settings_forbidden(self):
        client = self.login(TEST_USERNAME)
        response = client.get(self.edit_settings_url)
        self.assertContains(response, 'Access Forbidden', status_code=403)

    def test_revert_settings_forbidden(self):
        client = self.login(TEST_USERNAME)
        response = client.get(self.revert_settings_url)
        self.assertContains(response, 'Access Forbidden', status_code=403)
