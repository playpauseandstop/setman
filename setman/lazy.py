import copy

from setman.backends import SetmanBackend
from setman.exceptions import ImproperlyConfigured, SettingDoesNotExist
from setman.frameworks import SetmanFramework
from setman.utils import importlib, logger
from setman.utils.parsing import is_settings_container, parse_configs


__all__ = ('LazySettings', )


class LazySettings(object):
    """
    Simple proxy object that accessed database only when user needs to read
    some setting.
    """
    __slots__ = ('_available_settings_cache', '_backend', '_fail_silently',
                 '_framework', '_settings', '_parent', '_prefix')

    def __init__(self, settings=None, prefix=None, parent=None):
        """
        Initialize lazy settings instance.
        """
        self._settings = settings
        self._parent = parent
        self._prefix = prefix

        self._backend = parent._backend if parent else None
        self._framework = parent._framework if parent else None

    def __delattr__(self, name):
        if name.startswith('_'):
            return super(LazySettings, self).__delattr__(name)

        if name == 'available_settings':
            del self._available_settings_cache

        if not self._configured:
            self.autoconf()

        framework_settings = self._framework.settings

        if hasattr(framework_settings, name):
            delattr(framework_settings, name)
        elif name in self._backend.data:
            del self._backend.data[name]

        raise SettingDoesNotExist(name)

    def __getattr__(self, name):
        """
        Add support for getting settings keys as instance attribute.

        For first try, method tries to read settings from database, then from
        Django settings and if all fails try to return default value of
        available setting from configuration definition file if any.
        """
        if name.startswith('_'):
            return super(LazySettings, self).__getattr__(name)

        if name == 'available_settings':
            return self._available_settings_cache

        if not self._configured:
            self.autoconf()

        data, prefix = copy.deepcopy(self._backend.data), self._prefix
        framework_settings = self._framework.settings

        # Read app setting from database
        if prefix and prefix in data and name in data[prefix]:
            return data[prefix][name]
        # Read project setting from database
        elif name in data and not isinstance(data[name], dict):
            return data[name]
        # Or from framework settings
        elif hasattr(framework_settings, name):
            return getattr(framework_settings, name)
        # Or read default value from available settings
        elif hasattr(self._settings, name):
            mixed = getattr(self._settings, name)

            if is_settings_container(mixed):
                return LazySettings(mixed, name, self)

            return mixed.default

        # If cannot read setting - raise error
        raise SettingDoesNotExist(name)

    def __setattr__(self, name, value):
        """
        Add support of setting values to settings as instance attribute.
        """
        if name.startswith('_'):
            return super(LazySettings, self).__setattr__(name, value)

        if not self._configured:
            self.autoconf()

        data, prefix = copy.deepcopy(self._backend.data), self._prefix
        framework_settings = self._framework.settings

        # First of all try to setup value to framework setting
        if hasattr(framework_settings, name):
            setattr(framework_settings, name, value)
        # Then setup value to project setting
        elif not prefix:
            data[name] = value
        # And finally setup value to app setting
        else:
            if not prefix in data:
                data[prefix] = {}
            data[prefix][name] = value

        self._backend.data = data

    def autoconf(self):
        """
        Auto configure ``setman`` library.
        """
        # Do we work with Django?
        try:
            from django.conf import settings
            settings.SETTINGS_MODULE
        except ImportError:
            pass
        else:
            return self.configure(framework='setman.frameworks.django_setman')

        message = 'Not enough data to auto configure setman library. Please, '\
                  'call ``settings.configure`` manually.'
        logger.error(message)

        raise ImproperlyConfigured(message)

    def configure(self, backend=None, framework=None, **kwargs):
        """
        Setup which backend will be used for reading and saving settings data
        and which framework will be used for searching for available settings.
        """
        assert not self._configured, '``LazySettings`` instance already ' \
                                     'configured. Backend: %r, framework: ' \
                                     '%r' % (self._backend, self._framework)

        if framework:
            # Import framework module by the Python path
            try:
                framework_module = importlib.import_module(framework)
            except ImportError:
                message = 'Cannot import framework module from %r path' % \
                          framework
                logger.error(message)

                raise ImproperlyConfigured(message)

            # Load framework class from module if possible
            try:
                framework_klass = getattr(framework_module, 'Framework')
            except AttributeError, e:
                message = 'Cannot import framework class from %r module' % \
                          framework
                logger.error(message)

                raise ImproperlyConfigured(message)

            # Framework class should be an instance of ``SetmanFramework``
            if not issubclass(framework_klass, SetmanFramework):
                message = '%r is not a subclass of %r' % \
                          (framework_klass, SetmanFramework)
                logger.error(message)

                raise ImproperlyConfigured(message)
        else:
            # If no framework would be set - we will use default class
            framework_klass = SetmanFramework

        if backend:
            try:
                backend_module = importlib.import_module(backend)
            except ImportError, e:
                message = 'Cannot import backend module from %r path' % backend
                logger.error(message)

                raise ImproperlyConfigured(message)

            try:
                backend_klass = getattr(backend_module, 'Backend')
            except AttributeError, e:
                message = 'Cannot import backend class from %r module' % \
                          backend
                logger.error(message)

                raise ImproperlyConfigured(message)

            if not issubclass(backend_klass, SetmanBackend):
                message = '%r is not a subclass of %r' % \
                          (backend_klass, SetmanBackend)
                logger.error(message)

                raise ImproperlyConfigured(message)
        elif not framework_klass.default_backend:
            message = '%r framework hasn\'t predefined backend. Please, ' \
                      'configure it by yourself!' % framework_klass
            logger.error(message)

            raise ImproperlyConfigured(message)
        else:
            backend_klass = framework_klass.default_backend

        self._framework = framework_klass(**kwargs)
        self._settings = self._get_available_settings()

        backend_kwargs = kwargs.copy()
        backend_kwargs.update({'available_settings': self._settings,
                               'framework': self._framework})

        self._backend = backend_klass(**backend_kwargs)

    @property
    def error(self):
        """
        Return last validation error if any.
        """
        assert self._configured, '``LazySettings`` should be configured ' \
                                 'before validating.'
        return self._backend.error

    def is_valid(self):
        """
        Check whether current settings are valid or not.
        """
        assert self._configured, '``LazySettings`` should be configured ' \
                                 'before validating.'
        return self._backend.is_valid()

    def revert(self):
        """
        Revert settings to default values.
        """
        assert self._configured, '``LazySettings`` should be configured ' \
                                 'before reverting.'
        self._backend.revert()

    def save(self):
        """
        Save customized settings to the database.
        """
        assert self._configured, '``LazySettings`` should be configured ' \
                                 'before saving.'
        self._backend.save()

    @property
    def _configured(self):
        """
        Return ``True`` if ``LazySettings`` instance is properly configured.
        """
        return bool(self._backend) and bool(self._framework)

    def _get_available_settings(self):
        """
        Parse configuration definition files and read all available settings
        from its.
        """
        assert self._framework, '``LazySettings`` should have ``_framework`` '\
                                'attr before reading all available settings.'

        if self._parent:
            return self._parent.available_settings

        if not hasattr(self, '_available_settings_cache'):
            cache = parse_configs(self._framework)
            setattr(self, '_available_settings_cache', cache)

        return getattr(self, '_available_settings_cache')
