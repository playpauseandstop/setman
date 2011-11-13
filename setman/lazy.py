from django.conf import settings as django_settings

from setman.models import Settings
from setman.utils import AVAILABLE_SETTINGS


__all__ = ('LazySettings', )


class LazySettings(object):
    """
    Simple proxy object that accessed database only when user needs to read
    some setting.
    """
    _custom = None

    def __getattr__(self, name):
        """
        Add support for getting settings keys as instance attribute.

        For first try, method tries to read settings from database, then from
        Django settings and if all fails try to return default value of
        available setting from configuration definition file if any.
        """
        if name.startswith('_'):
            return super(LazySettings, self).__getattr__(name)

        if self._custom is None:
            self._custom = self._get_custom_settings()

        # Read setting from database
        if name in self._custom.data:
            return self._custom.data.get(name)
        # Or from Django settings
        elif hasattr(django_settings, name):
            return getattr(django_settings, name)
        # Or read default value from available settings
        elif hasattr(AVAILABLE_SETTINGS, name):
            return getattr(AVAILABLE_SETTINGS, name).default

        # If cannot read setting - raise error
        raise AttributeError('Settings has not attribute %r' % name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return super(LazySettings, self).__setattr__(name, value)

        if hasattr(django_settings, name):
            setattr(django_settings, name, value)
        else:
            if self._custom is None:
                self._custom = self._get_custom_settings()
            setattr(self._custom, name, value)

    def save(self):
        """
        Save customized settings to the database.
        """
        if self._custom is None:
            self._custom = self._get_custom_settings()
        self._custom.save()

    def _clear(self):
        self._custom = None

    def _get_custom_settings(self):
        try:
            return Settings.objects.get()
        except Settings.DoesNotExist:
            return Settings.objects.create(data={})
