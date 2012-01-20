import os

from django import forms as django_forms
from django.conf import settings as django_settings
from django.core.exceptions import ValidationError
from django.db.models.loading import get_apps

from setman.backends.django import Backend as DjangoBackend
from setman.frameworks import SetmanFramework
from setman.utils import DEFAULT_SETTINGS_FILENAME, importlib


class Framework(SetmanFramework):
    """
    Add support of Django framework for ``setman`` library.
    """
    auth_permitted_func = lambda request: request.user.is_superuser
    default_backend = DjangoBackend
    field_klasses = {
        'boolean': django_forms.BooleanField,
        'choice': django_forms.ChoiceField,
        'decimal': django_forms.DecimalField,
        'float': django_forms.FloatField,
        'int': django_forms.IntegerField,
        'string': django_forms.CharField,
    }
    settings = django_settings
    ValidationError = ValidationError

    def __init__(self, **kwargs):
        """
        Read setman settings from django settings if possible.
        """
        conf = lambda key, value=None: getattr(django_settings, key, value)

        defaults = {
            'additional_types': conf('SETMAN_ADDITIONAL_TYPES', ()),
            'auth_permitted_func': conf('SETMAN_AUTH_PERMITTED',
                                        self.auth_permitted_func),
            'default_values_file': conf('SETMAN_DEFAULT_VALUES_FILE'),
            'settings_file': conf('SETMAN_SETTINGS_FILE'),
            'settings_files': conf('SETMAN_SETTINGS_FILES', {}),
        }
        defaults.update(kwargs)

        super(Framework, self).__init__(**defaults)

    def find_settings_files(self):
        """
        Find configuration definition files from each available installed app
        and from project itself.
        """
        apps = get_apps()
        files = {}
        pathes = self.settings_files

        for app in apps:
            app_name = app.__name__.split('.')[-2]
            path = pathes.get(app_name, DEFAULT_SETTINGS_FILENAME)

            if not os.path.isabs(path):
                dirname = os.path.dirname(app.__file__)
                path = os.path.join(dirname, path)

            if not os.path.isfile(path):
                continue

            files.update({app_name: path})

        for app_name, path in pathes.iteritems():
            if name in files or not os.path.isfile(path):
                continue

            files.update({app_name: path})

        path = self.settings_file or DEFAULT_SETTINGS_FILENAME

        # If path isn't absolute - made it
        if not os.path.isabs(path):
            module = importlib.import_module(django_settings.SETTINGS_MODULE)
            dirname = os.path.dirname(os.path.normpath(module.__file__))
            path = os.path.join(dirname, path)

        files.update({'__project__': path})

        return files

    def setting_field_klass(self, setting):
        """
        """
        if setting.type == 'string' and setting.regex:
            return django_forms.RegexField
        return super(Framework, self).setting_field_klass(setting)

    def setting_to_field(self, setting):
        """
        """
        field = super(Framework, self).setting_to_field(setting)

        if setting.builtin_validators:
            field.validators = \
                list(set(setting.validators).\
                     difference(set(setting.builtin_validators)))

        return field
