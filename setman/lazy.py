from django.conf import settings as django_settings

from setman.models import Settings
from setman.utils import AVAILABLE_SETTINGS, is_settings_container


__all__ = ('LazySettings', )


class LazySettings(object):
    """
    Simple proxy object that accessed database only when user needs to read
    some setting.
    """
    __slots__ = ('_custom_cache', '_settings', '_parent', '_prefix')

    def __init__(self, settings=None, prefix=None, parent=None):
        """
        Initialize lazy settings instance.
        """
        self._settings = settings or AVAILABLE_SETTINGS
        self._parent = parent
        self._prefix = prefix

    def __delattr__(self, name):
        if name.startswith('_'):
            return super(LazySettings, self).__delattr__(name)

        if hasattr(django_settings, name):
            delattr(django_settings, name)
        else:
            delattr(self._custom, name)

    def __getattr__(self, name):
        """
        Add support for getting settings keys as instance attribute.

        For first try, method tries to read settings from database, then from
        Django settings and if all fails try to return default value of
        available setting from configuration definition file if any.
        """
        if name.startswith('_'):
            return super(LazySettings, self).__getattr__(name)

        data, prefix = self._custom.data, self._prefix

        # Read app setting from database
        if prefix and prefix in data and name in data[prefix]:
            return data[prefix][name]
        # Read project setting from database
        elif name in data and not isinstance(data[name], dict):
            return data[name]
        # Or from Django settings
        elif hasattr(django_settings, name):
            return getattr(django_settings, name)
        # Or read default value from available settings
        elif hasattr(self._settings, name):
            mixed = getattr(self._settings, name)

            if is_settings_container(mixed):
                return LazySettings(mixed, name, self)

            return mixed.default

        # If cannot read setting - raise error
        raise AttributeError('Settings has not attribute %r' % name)

    def __setattr__(self, name, value):
        """
        Add support of setting values to settings as instance attribute.
        """
        if name.startswith('_'):
            return super(LazySettings, self).__setattr__(name, value)

        # First of all try to setup value to Django setting
        if hasattr(django_settings, name):
            setattr(django_settings, name, value)
        # Then setup value to project setting
        elif not self._prefix:
            setattr(self._custom, name, value)
        # And finally setup value to app setting
        else:
            data, prefix = self._custom.data, self._prefix

            if not prefix in data:
                data[prefix] = {}

            data[prefix].update({name: value})

    def revert(self):
        """
        Revert settings to default values.
        """
        self._custom.revert()

    def save(self):
        """
        Save customized settings to the database.
        """
        self._custom.save()

    def _clear(self):
        """
        Clear custom settings cache.
        """
        if hasattr(self, '_custom_cache'):
            delattr(self, '_custom_cache')

    @property
    def _custom(self):
        if self._parent:
            return self._parent._custom

        if not hasattr(self, '_custom_cache'):
            setattr(self, '_custom_cache', self._get_custom_settings())

        return getattr(self, '_custom_cache')

    def _get_custom_settings(self):
        """
        Do not read any settings before post_syncdb signal is called.
        """
        try:
            return Settings.objects.get()
        except Settings.DoesNotExist:
            return Settings.objects.create(data={})
