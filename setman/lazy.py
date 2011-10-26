from django.conf import settings as django_settings

from setman.models import Settings


__all__ = ('LazySettings', )


class LazySettings(object):
    """
    Simple proxy object that accessed database only when user needs to read
    some setting.
    """
    _custom = None

    def __getattr__(self, name):
        if not name.isupper():
            return super(LazySettings, self).__getattr__(name)

        if self._custom is None:
            self._custom = self._get_custom_settings()

        if name in self._custom.data:
            return self._custom.data.get(name)
        elif hasattr(django_settings, name):
            return getattr(django_settings, name)

        raise AttributeError('Settings has not attribute %r' % name)

    def __setattr__(self, name, value):
        if not name.isupper():
            return super(LazySettings, self).__setattr__(name, value)

        if hasattr(django_settings, name):
            setattr(django_settings, name, value)
        else:
            if self._custom is None:
                self._custom = self._get_custom_settings()
            setattr(self._custom, name, value)

    def save(self):
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
