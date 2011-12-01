import copy
import logging
import os
import re

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from ConfigParser import Error as ConfigParserError, SafeConfigParser
from decimal import Decimal

from django import forms
from django.conf import settings as django_settings
from django.db.models.loading import get_apps, get_model
from django.utils import importlib
from django.utils.datastructures import SortedDict


__all__ = ('AVAILABLE_SETTINGS', 'auth_permitted', 'parse_config')


DEFAULT_SETTINGS_FILENAME = 'settings.cfg'
logger = logging.getLogger('setman')


class ConfigParser(SafeConfigParser, object):
    """
    Customize default behavior for config parser instances to support config
    files without sections at all.
    """
    no_sections_mode = False
    optionxform = lambda _, value: value

    def _read(self, fp, fpname):
        """
        If "No Sections Mode" enabled - add global section as first line of
        file handler.
        """
        if self.no_sections_mode:
            global_section = StringIO()
            global_section.write('[DEFAULT]\n')
            global_section.write(fp.read())
            global_section.seek(0)
            fp = global_section

        return super(ConfigParser, self)._read(fp, fpname)


class Setting(object):
    """
    Base class for setting values that can provided in configuration definition
    file.

    The class has next attributes:

    * ``name``
    * ``type``
    * ``default``
    * ``required``
    * ``label``
    * ``help_text``
    * ``validators``
    * ``field``
    * ``field_args``
    * ``field_kwargs``

    The last three attributes can be provided only in Python module, when all
    other attrs can read from configuration definition file.
    """
    app_name = None
    default = None
    field_args = ('label', 'help_text', 'initial', 'required', 'validators')
    field_klass = None
    field_kwargs = {}
    help_text = None
    label = None
    name = None
    required = True
    type = None
    validators = None

    def __init__(self, **kwargs):
        """
        Initialize setting.
        """
        self.app_name = kwargs.pop('app_name', None)
        self.update(**kwargs)

    def __repr__(self):
        return u'<%s: %s>' % (self.__class__.__name__, self.__unicode__())

    def __unicode__(self):
        return u'%s = %r' % (self.name, self.initial)

    @property
    def initial(self):
        """
        Read real setting value from database or if impossible - just send
        default setting value.
        """
        from setman import settings

        if self.app_name:
            settings = getattr(settings, self.app_name)

        return getattr(settings, self.name, self.default)

    def to_field(self, **kwargs):
        """
        Convert current setting instance to form field.

        You should provide ``kwargs`` and all values from here would be used
        when initing ``field`` instance instead of ``Setting`` attributes.
        """
        if not self.field_klass:
            raise ValueError('Please, supply `field_klass` attribute first.')

        field_kwargs = {}

        for arg in self.field_args:
            value = kwargs[arg] if arg in kwargs else getattr(self, arg)
            field_kwargs.update({arg: value})

        field_kwargs.update(**self.field_kwargs)
        return self.field_klass(**field_kwargs)

    def to_python(self, value):
        """
        Convert setting value to necessary Python type. By default, returns
        same value without any conversion.
        """
        return value

    def update(self, **kwargs):
        """
        Update attributes for current setting instance.
        """
        self._validators = kwargs.pop('validators', None)
        restricted = ('field_klass', 'field_args', 'field_kwargs',
                      'validators')

        for key, _ in kwargs.items():
            if not hasattr(self, key):
                kwargs.pop(key)

            if key in restricted:
                kwargs.pop(key)

        self.__dict__.update(kwargs)
        self.required = force_bool(self.required)

    @property
    def validators(self):
        """
        Lazy loaded validators.
        """
        cache_key = '_validators_cache'
        if not hasattr(self, cache_key):
            setattr(self, cache_key, self._parse_validators(self._validators))
        return getattr(self, cache_key)

    def _parse_validators(self, value):
        """
        Parse validators string and try to convert it to list with actual
        validator functions.
        """
        if not value:
            return []

        items = map(lambda item: item.strip(), value.split(','))
        validators = []

        for item in items:
            try:
                validator = load_from_path(item)
            except (AttributeError, ImportError):
                logger.exception('Cannot load %r validator for %s setting.',
                                 item, self.name)
                continue

            validators.append(validator)

        return validators


class SettingTypeDoesNotExist(Exception):
    """
    Simple exception that raised when user tried to load not supported setting
    type from configuration definition file.
    """


class BooleanSetting(Setting):
    """
    Boolean setting.
    """
    field_klass = forms.BooleanField
    required = False
    type = 'boolean'

    def to_python(self, value):
        """
        Convert string to the boolean type.
        """
        return force_bool(value)

    def update(self, **kwargs):
        super(BooleanSetting, self).update(**kwargs)
        self.default = self.to_python(self.default)


class ChoiceSetting(Setting):
    """
    Choice setting.
    """
    choices = None
    field_args = Setting.field_args + ('choices', )
    field_klass = forms.ChoiceField
    type = 'choice'

    @property
    def choices(self):
        """
        Lazy loaded choices.
        """
        cache_key = '_choices_cache'
        if not hasattr(self, cache_key):
            setattr(self, cache_key, self._parse_choices(self._choices))
        return getattr(self, cache_key)

    def _parse_choices(self, value):
        """
        Convert string value to valid choices tuple.

        **Supported formats:**

        * a, b, c
        * (a, A), (b, B), (c, C)
        * a { b, c }, d { e, f }
        * A { (b, B), (c, C) }, D { (e, E), (f, F) }
        * path.to.CHOICES
        * path.to.Model.CHOICES
        * app.Model.CHOICES

        """
        # Start parsing with internal choices
        if not ',' in value and '.' in value:
            # Choices tuple should be last part of value
            path, attr = value.rsplit('.', 1)

            # Try to process path as ``app.Model`` definition
            model = None

            try:
                app, model = path.split('.')
            except ValueError:
                pass
            else:
                model = get_model(app, model)

            # If cannot process path as ``app.Model`` just load it as module
            # or as class from module
            if model is None:
                try:
                    module = importlib.import_module(path)
                except ImportError:
                    try:
                        module = load_from_path(path)
                    except (AttributeError, ImportError):
                        logger.exception('Cannot load choices from %r path',
                                         value)
                        return ()
            else:
                module = model

            # And finally, try to get choices attr in module or model
            try:
                choices = getattr(module, attr)
            except AttributeError:
                logger.exception('Cannot load choices from %r path', value)
                return ()
        elif not '{' in value and not '}' in value:
            # Parse choice with labels
            label_re = re.compile(r'\(([^,]+),\s+([^\)]+)\)', re.M)
            found = label_re.findall(value)

            if found:
                choices = found
            # If nothing found by regex, just split value by comma and
            # duplicate resulted items
            else:
                choices = map(lambda item: (item.strip(), item.strip()),
                              value.split(','))
        else:
            # Parse groups
            groups_re = re.compile(r'([^{]+){([^}]+)},?', re.M)
            found = groups_re.findall(value)

            if found:
                choices = []

                for group, data in found:
                    group = group.strip()
                    choices.append((group, self._parse_choices(data.strip())))
            else:
                logger.error('Cannot parse choices from %r', value)
                return ()

        return tuple(choices)

    def update(self, **kwargs):
        self._choices = kwargs.pop('choices', None)
        super(ChoiceSetting, self).update(**kwargs)


class DecimalSetting(Setting):
    """
    Decimal setting.
    """
    decimal_places = None
    field_args = Setting.field_args + ('decimal_places', 'max_digits',
                                       'max_value', 'min_value')
    field_klass = forms.DecimalField
    max_digits = None
    max_value = None
    min_value = None
    type = 'decimal'

    def to_python(self, value):
        if value is None:
            return value
        return Decimal(str(value))

    def update(self, **kwargs):
        super(DecimalSetting, self).update(**kwargs)

        int_setting = IntSetting()
        self.decimal_places = int_setting.to_python(self.decimal_places)
        self.max_digits = int_setting.to_python(self.max_digits)

        self.default = self.to_python(self.default)
        self.max_value = self.to_python(self.max_value)
        self.min_value = self.to_python(self.min_value)


class IntSetting(Setting):
    """
    Integer setting.
    """
    field_args = Setting.field_args + ('max_value', 'min_value')
    field_klass = forms.IntegerField
    max_value = None
    min_value = None
    type = 'int'

    def to_python(self, value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def update(self, **kwargs):
        super(IntSetting, self).update(**kwargs)
        self.default = self.to_python(self.default)
        self.max_value = self.to_python(self.max_value)
        self.min_value = self.to_python(self.min_value)


class FloatSetting(IntSetting):
    """
    Float setting.
    """
    field_klass = forms.FloatField
    type = 'float'

    def to_python(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


class StringSetting(Setting):
    """
    String setting.
    """
    field_args = Setting.field_args + ('max_length', 'min_length')
    field_klass = forms.CharField
    max_length = None
    min_length = None
    regex = None
    type = 'string'

    def to_field(self, **kwargs):
        """
        Use ``RegexField`` for string setting if ``regex`` was filled in
        configuration definition file.
        """
        if self.regex:
            if not 'regex' in self.field_args:
                self.field_args = self.field_args + ('regex', )
            self.field_klass = forms.RegexField
        return super(StringSetting, self).to_field(**kwargs)


class SettingsContainer(object):
    """
    Simple settings container. Could be two types: global and local.

    When global mode enabled, can add local settings container as attribute,
    when local only can add settings (not container) as attributes.
    """
    def __init__(self, path=None, app_name=None):
        self._data = []
        self.app_name = app_name
        self.path = path

    def __iter__(self):
        return (item for item in self._data)

    def __len__(self):
        return len(self._data)

    def add(self, name, value):
        if name == '__project__':
            for setting in value:
                self.add(setting.name, setting)
        else:
            self._data.append(value)
            setattr(self, name, value)


def auth_permitted(user):
    """
    Check that the user can have access to the view.
    """
    default = lambda user: user.is_superuser
    func = getattr(django_settings, 'SETMAN_AUTH_PERMITTED', default)
    return func(user)



def data_to_setting(data, additional_types=None):
    """
    Convert data dict to setting instance.
    """
    additional_types = additional_types or []
    setting = None
    setting_type = data.get('type')

    all_values = globals().values() + additional_types

    for value in all_values:
        try:
            if not issubclass(value, Setting):
                continue
        except TypeError:
            continue

        if not value.type or not setting_type or \
           value.type.lower() != setting_type.lower():
            continue

        setting = value(**data)

    if setting is None:
        raise SettingTypeDoesNotExist('%r setting type not found.' % \
                                      setting_type)

    return setting


def force_bool(value):
    """
    Convert string value to boolean instance.
    """
    if isinstance(value, (bool, int)):
        return bool(value)

    boolean_states = ConfigParser._boolean_states
    if not value.lower() in boolean_states:
        return None

    return boolean_states[value.lower()]


def is_settings_container(value):
    """
    Return if ``value`` is ``SettingsContainer`` or ``LazySettings`` instance
    or not.
    """
    try:
        klass_name = value.__class__.__name__
    except:
        klass_name = ''

    return isinstance(value, SettingsContainer) or klass_name == 'LazySettings'


def load_from_path(path):
    """
    Load class or function from string path.
    """
    module, attr = path.rsplit('.', 1)
    mod = importlib.import_module(module)
    return getattr(mod, attr)


def parse_config(path, additional_types=None, default_values=None,
                 app_name=None, all_settings=None):
    """
    Parse Configuration Definition File.

    In most cases this file needs to be placed in same folder where project
    settings module exist and named as ``settings.cfg``.

    But you can customize things with using ``SETMAN_SETTINGS_FILE`` option.
    Provide there path where settings file actually placed.

    Also current function can called with ``path`` string.
    """
    # If path isn't absolute - made it
    if not os.path.isabs(path):
        module = importlib.import_module(django_settings.SETTINGS_MODULE)
        dirname = os.path.dirname(os.path.normpath(module.__file__))
        path = os.path.join(dirname, path)

    config = ConfigParser(dict_type=SortedDict)
    empty_settings = SettingsContainer(path, app_name)

    try:
        config.read(path)
    except ConfigParserError:
        logger.exception('Cannot parse configuration definition file from ' \
                         '%r', path)
        return empty_settings

    settings = copy.deepcopy(empty_settings)

    for setting in config.sections():
        if '.' in setting:
            full_setting = setting
            app_name, setting = setting.split('.', 1)

            try:
                app_settings = getattr(all_settings, app_name)
            except AttributeError:
                logger.exception('Cannot find settings for %r app', app_name)
                continue

            try:
                app_setting = getattr(app_settings, setting)
            except AttributeError:
                logger.exception('Cannot find %r app setting %r',
                                 app_name, setting)

            data = dict(config.items(full_setting))

            if default_values and full_setting in default_values:
                data.update({'default': default_values[setting]})

            try:
                app_setting = update_app_setting(app_setting, data)
            except ValueError:
                logger.exception('Cannot redefine ``type`` attr for %r ' \
                                 'setting', full_setting)
                continue
        else:
            data = dict(config.items(setting))
            data.update({'app_name': app_name, 'name': setting})

            if default_values and setting in default_values:
                data.update({'default': default_values[setting]})

            try:
                setting = data_to_setting(data, additional_types)
            except SettingTypeDoesNotExist:
                logger.exception('Cannot find proper setting class for %r ' \
                                 'type', data.get('type'))
                return empty_settings

            settings.add(setting.name, setting)

    return settings


def parse_configs():
    """
    Parse all available config definition files as for all availbale apps and
    for project itself at last.

    Also we need to read additional types and additional default values before
    parsing start.
    """
    additional_types = getattr(django_settings, 'SETMAN_ADDITIONAL_TYPES', ())
    additional_setting_types = []
    all_settings = SettingsContainer()
    default_values = {}

    for item in additional_types:
        try:
            additional_type = load_from_path(item)
        except (AttributeError, TypeError):
            logger.exception('Cannot load %r additional setting type from ' \
                             'configuration', item)

        additional_setting_types.append(additional_type)

    additional_types = additional_setting_types

    # Use ``SortedDict`` instance for reading sections on config file instead
    # of default ``dict`` that can shuffle the sections.
    config = ConfigParser(dict_type=SortedDict)

    # First we need to read default values file
    default_values_file = \
        getattr(django_settings, 'SETMAN_DEFAULT_VALUES_FILE', None)

    if default_values_file:
        config.no_sections_mode = True

        try:
            config.read(default_values_file)
        except ConfigParserError:
            logger.exception('Cannot read default values from %r',
                             default_values_file)
        else:
            default_values = config.defaults()
        finally:
            config.no_sections_mode = False

    # Then try to load all available configuration definition files from all
    # installed apps
    apps = get_apps()

    # Don't forget to read pathes to app configuration definition files from
    # Django settings
    pathes = getattr(django_settings, 'SETMAN_SETTINGS_FILES', {})

    for app in apps:
        app_name = app.__name__.split('.')[-2]
        path = pathes.get(app_name, DEFAULT_SETTINGS_FILENAME)

        if not os.path.isabs(path):
            dirname = os.path.dirname(app.__file__)
            path = os.path.join(dirname, path)

        if not os.path.isfile(path):
            continue

        settings = \
            parse_config(path, additional_types, default_values, app_name)
        all_settings.add(app_name, settings)

    # And finally read project configuration definition file if any
    path = getattr(django_settings, 'SETMAN_SETTINGS_FILE', None)
    path = DEFAULT_SETTINGS_FILENAME if path is None else path

    settings = parse_config(path, additional_types, default_values,
                            all_settings=all_settings)
    all_settings.add('__project__', settings)
    all_settings.path = settings.path

    return all_settings


def update_app_setting(setting, data):
    """
    Update app setting from the project configuration definition file.
    """
    kwargs = {}

    for key, value in data.items():
        if key == 'type':
            raise ValueError('Setting `type` attribute denied to update')

        kwargs[key] = value

    setting.update(**kwargs)
    return setting


AVAILABLE_SETTINGS = parse_configs()
