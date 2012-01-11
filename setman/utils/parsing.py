import copy

from setman.exceptions import SettingTypeDoesNotExist
from setman.utils import ConfigParser, ConfigParserError, logger, \
    types as setting_types
from setman.utils.ordereddict import OrderedDict
from setman.utils.types import SetmanSetting


__all__ = ('is_settings_container', )


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


def data_to_setting(data, additional_types=None):
    """
    Convert data dict to setting instance.
    """
    additional_types = list(additional_types or [])
    setting = None
    setting_type = data.get('type')

    all_values = dir(setting_types) + additional_types

    for value in all_values:
        if isinstance(value, basestring):
            value = getattr(setting_types, value)

        try:
            if not issubclass(value, SetmanSetting):
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
    config = ConfigParser(dict_type=OrderedDict)
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
                continue

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


def parse_configs(framework):
    """
    Parse all available config definition files as for all availbale apps and
    for project itself at last.

    Also we need to read additional types and additional default values before
    parsing start.
    """
    additional_types = framework.get_additional_types()
    all_settings = SettingsContainer()
    default_values = {}
    fail_silently = framework.fail_silently

    # Use ``OrderedDict`` instance for reading sections on config file instead
    # of default ``dict`` that can shuffle the sections.
    config = ConfigParser(dict_type=OrderedDict)

    # First we need to read default values file
    default_values_file = framework.find_default_values_file()

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

    # Read available settings files from framework
    pathes = framework.find_settings_files()

    for app_name, path in pathes.items():
        if app_name == '__project__':
            continue

        settings = \
            parse_config(path, additional_types, default_values, app_name)
        all_settings.add(app_name, settings)

    # And finally read project configuration definition file if any
    path = pathes.get('__project__')

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
