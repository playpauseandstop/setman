import os

from setman.exceptions import ValidationError
from setman.utils import DEFAULT_SETTINGS_FILENAME, load_from_path, logger
from setman.utils.ordereddict import OrderedDict
from setman.utils.parsing import is_settings_container


__all__ = ('SetmanFramework', )


class SetmanCache(object):

    def __init__(self):
        self.data = {}

    def delete(self, name):
        del self.data[name]

    def get(self, name):
        return self.data.get(name)

    def set(self, name, value, *args, **kwargs):
        self.data[name] = value


class SetmanFramework(object):
    """
    Base object for any framework that would be supported by ``setman`` app.

    Main purpose of this object is providing necessary methods which would be
    used when ``setman`` will be trying to parse configuration definition
    files.

    Also, you could setup default backend for framework.
    """
    auth_permitted_func = None
    default_backend = None
    field_klasses = None
    field_name_separator = '.'
    settings = type('SetmanSettings', (object, ), {})
    ValidationError = ValidationError

    def __init__(self, settings_file=None, settings_files=None,
                 default_values_file=None, additional_types=None, **kwargs):
        """
        Setup necessary params for setman supported framework.
        """
        self.additional_types = additional_types
        self.default_values_file = default_values_file
        self.settings_file = settings_file
        self.settings_files = settings_files
        self.fail_silently = kwargs.pop('fail_silently', True)

        if 'default_backend' in kwargs:
            kwargs.pop('default_backend')

        if 'settings' in kwargs:
            kwargs.pop('settings')

        self.__dict__.update(kwargs)

    def build_form_fields(self, available_settings=None, fields=None):
        """
        Build fields from list of availabale settings.
        """
        from setman import settings

        available_settings = available_settings or settings.available_settings
        fields = fields or OrderedDict()

        for setting in available_settings:
            if is_settings_container(setting):
                fields = self.build_form_fields(setting, fields)
            else:
                field = settings._framework.setting_to_field(setting)
                fields[field.name] = field

        return fields

    def get_additional_types(self):
        """
        Return tuple of additional types that would be supported when parsing
        config definition files.
        """
        additional_types = self.additional_types or ()
        types = []

        for item in additional_types:
            try:
                additional_type = load_from_path(item)
            except (AttributeError, TypeError):
                logger.exception('Cannot load %r additional setting type ' \
                                 'from configuration', item)
                continue

            types.append(additional_type)

        return tuple(types)

    def find_default_values_file(self):
        """
        Return path for default values file.
        """
        return self.default_values_file

    def find_settings_files(self):
        """
        Return dict of possible configuration definition files.
        """
        files = self.settings_files or {}
        files.update({
            '__project__': self.settings_file or DEFAULT_SETTINGS_FILENAME
        })

        for key, value in files.items():
            if os.path.isabs(value):
                continue

            files[key] = os.path.abspath(value)

        return files

    def save_form_fields(self, data):
        """
        """
        from setman import settings
        sep = self.field_name_separator

        for key, value in data.items():
            if sep in key:
                app_name, key = key.split(sep, 1)
                setattr(getattr(settings, app_name), key, value)
            else:
                setattr(settings, key, value)

        settings.save()

    def setting_field_klass(self, setting):
        """
        Return field class for the specified setting.
        """
        if not self.field_klasses:
            return None
        return self.field_klasses.get(setting.type, None)

    def setting_to_field(self, setting, **kwargs):
        """
        Convert setting instance to form field.

        You should provide ``kwargs`` and all values from here would be used
        when initing ``field`` instance instead of ``Setting`` attributes.
        """
        field_klass = setting.field_klass or self.setting_field_klass(setting)

        if not field_klass:
            raise ValueError('Please, supply `field_klass` attribute to %r ' \
                             'instance first.' % setting)

        field_args = setting.get_field_args()
        field_kwargs = {}

        for arg in field_args:
            value = kwargs[arg] if arg in kwargs else getattr(setting, arg)
            field_kwargs.update({arg: value})

        field_kwargs.update(**setting.get_field_kwargs())
        field_kwargs = self.translate_field_kwargs(field_kwargs)

        field = field_klass(**field_kwargs)
        field.app_name = setting.app_name
        field.name_app = setting.app_name[::-1] if setting.app_name else None

        if setting.app_name:
            sep = self.field_name_separator
            field.name = sep.join((setting.app_name, setting.name))
        else:
            field.name = setting.name

        return field

    def translate_field_kwargs(self, kwargs):
        """
        Provide specific field keyword argument translation from Django forms
        library to library used by current framework.
        """
        return kwargs
