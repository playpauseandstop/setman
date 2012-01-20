from setman.exceptions import ValidationError
from setman.utils.parsing import is_settings_container


__all__ = ('SetmanBackend', )


class SetmanBackend(object):
    """
    How ``setman`` library will interact with the data storage.
    """
    available_settings = None
    data_cache_key = '_data_cache'
    framework = None
    ignore_cache = False

    def __init__(self, **kwargs):
        """
        Initialize backend object and read settings from data storage.
        """
        # Copy all keyword arguments to the instance scope. But ignore ``data``
        # keyword if any.
        if 'data' in kwargs:
            kwargs.pop('data')

        self.__dict__.update(kwargs)

    def __getattribute__(self, name):
        """
        Deny ability of saving invalid data.
        """
        if name != 'save':
            return super(SetmanBackend, self).__getattribute__(name)

        if hasattr(self, 'error'):
            raise ValueError('Cannot save invalid settings.')

        return super(SetmanBackend, self).__getattribute__(name)

    def clear(self):
        """
        Clear data cache from backend instance if any.
        """
        del self.data

        if hasattr(self, 'error'):
            delattr(self, 'error')

    @property
    def data(self):
        """
        Simple way to read backend data.
        """
        ignore_cache = self.ignore_cache

        if not hasattr(self, self.data_cache_key) or ignore_cache:
            value = self._batch_method('to_python', self.read())
            setattr(self, self.data_cache_key, value)

        return getattr(self, self.data_cache_key)

    @data.deleter
    def data(self):
        """
        Invalidate backend data.
        """
        if hasattr(self, self.data_cache_key):
            delattr(self, self.data_cache_key)

    @data.setter
    def data(self, value):
        """
        Assign new data to the backend.
        """
        value = self._batch_method('to_python', value)
        setattr(self, self.data_cache_key, value)

    def is_valid(self, prefix=None):
        """
        Validate every setting before save.
        """
        try:
            self._batch_method('validate', self.data)
        except self.framework.ValidationError, e:
            setattr(self, 'error', e)
            return False
        else:
            if hasattr(self, 'error'):
                delattr(self, 'error')

        return True

    def read(self):
        """
        Read settings from data storage.

        Should return ``dict``-compatible instance which would be stored to
        ``data`` attribute.
        """
        raise NotImplementedError

    def revert(self, prefix=None):
        """
        Revert all available settings to default values.
        """
        available_settings = self.available_settings
        available_settings = \
            getattr(available_settings, prefix) if prefix \
                                                else available_settings
        data = {}

        for mixed in available_settings:
            if is_settings_container(mixed):
                app_name = mixed.app_name
                data.update({app_name: self.revert(app_name)})
            else:
                data.update({mixed.name: mixed.default})

        if prefix:
            return data

        self.data = data
        self.save()

    def save(self):
        """
        Save current settings data to the data storage.
        """
        raise NotImplementedError

    def _batch_method(self, method, data, prefix=None):
        """
        Run batch ``method`` for data.
        """
        available_settings = self.available_settings

        if prefix:
            available_settings = getattr(available_settings, prefix)

        for key, value in data.items():
            if not hasattr(available_settings, key):
                continue

            mixed = getattr(available_settings, key)

            if is_settings_container(mixed):
                data[key] = self._batch_method(method, value, key)
            else:
                data[key] = getattr(mixed, method)(value)

        return data
