import inspect
import os

from wtforms import fields as wtf_fields, validators as wtf_validators

from setman.frameworks import SetmanFramework
from setman.frameworks.flask_setman.blueprint import setman_blueprint
from setman.frameworks.flask_setman.fields import SelectField
from setman.frameworks.flask_setman.validators import Required
from setman.utils import DEFAULT_SETTINGS_FILENAME


class Framework(SetmanFramework):
    """
    Add support of Flask framework using WTForms for editing fields in UI.
    """
    field_klasses = {
        'boolean': wtf_fields.BooleanField,
        'choice': SelectField,
        'decimal': wtf_fields.DecimalField,
        'float': wtf_fields.FloatField,
        'int': wtf_fields.IntegerField,
        'string': wtf_fields.TextField,
    }
    field_name_separator = '__'
    ValidationError = wtf_validators.ValidationError

    def __init__(self, **kwargs):
        """
        We need to specify ``app`` keyword argument to add support of Flask
        framework for ``setman`` library.

        Also, try to read global settings from ``app.config`` dict.
        """
        if not 'app' in kwargs:
            raise TypeError('Please, supply ``app`` keyword arg first.')

        self.flask_app = kwargs.pop('app')
        app = self.flask_app
        conf = lambda app, key, value=None: app.config.get(key, value)

        defaults = {
            'additional_types': conf(app, 'SETMAN_ADDITIONAL_TYPES', ()),
            'auth_permitted_func': conf(app,
                                        'SETMAN_AUTH_PERMITTED',
                                        self.auth_permitted_func),
            'default_values_file': conf(app, 'SETMAN_DEFAULT_VALUES_FILE'),
            'settings_file': conf(app, 'SETMAN_SETTINGS_FILE'),
            'settings_files': conf(app, 'SETMAN_SETTINGS_FILES', {}),
        }
        defaults.update(kwargs)

        super(Framework, self).__init__(**defaults)

        # Don't forget to register setman blueprint and add support of ability
        # to change settings via UI
        app.register_blueprint(setman_blueprint, url_prefix='/setman')

    def find_settings_files(self):
        """
        Find configuration definition files from each available installed
        blueprint and from project itself.
        """
        blueprints = self.flask_app.blueprints
        files = {}
        pathes = self.settings_files

        for name, blueprint in blueprints.iteritems():
            path = pathes.get(name, DEFAULT_SETTINGS_FILENAME)

            if not os.path.isabs(path):
                dirname = os.path.dirname(blueprint.root_path)
                path = os.path.join(dirname, path)

            if not os.path.isfile(path):
                continue

            files.update({name: path})

        for name, path in pathes.iteritems():
            if name in files or not os.path.isfile(path):
                continue

            files.update({name: path})

        path = self.settings_file or DEFAULT_SETTINGS_FILENAME

        # If path isn't absolute - made it
        if not os.path.isabs(path):
            dirname = self.flask_app.root_path
            path = os.path.join(dirname, path)

        files.update({'__project__': path})
        return files

    @property
    def settings(self):
        """
        Convert Flask's config dict to something like Django settings instance.
        """
        return SetmanSettings(self.flask_app.config)

    def translate_field_kwargs(self, kwargs):
        """
        Translate Django forms field kwargs to WTForms field kwargs.
        """
        arg_replacements = (
            ('decimal_places', 'places'),
            ('help_text', 'description'),
            ('initial', 'default'),
        )

        args_to_validators = (
            ('regex', lambda value: wtf_validators.Regexp(regex=value)),
            ('required', lambda value: Required() if value \
                                           else wtf_validators.Optional()),
        )

        delete_args = ('max_digits', 'max_length', 'max_value', 'min_length',
                       'min_value')

        def wtforms_validator(validator_func):
            def validator(form, field):
                return validator_func(field.data)
            return validator

        for old_key, new_key in arg_replacements:
            if not old_key in kwargs:
                continue

            value = kwargs.pop(old_key)
            kwargs.update({new_key: value})

        for key, trigger in args_to_validators:
            if not key in kwargs:
                continue

            value = kwargs.pop(key)

            if not 'validators' in kwargs:
                kwargs['validators'] = []

            kwargs['validators'].append(trigger(value))

        for key in delete_args:
            if not key in kwargs:
                continue

            del kwargs[key]

        validators_list = []

        for validator_func in kwargs['validators']:
            if inspect.isfunction(validator_func):
                spec = inspect.getargspec(validator_func)

                if len(spec.args) == 1:
                    validator_func = wtforms_validator(validator_func)

            validators_list.append(validator_func)

        kwargs.update({'validators': validators_list})
        return kwargs


class SetmanSettings(object):
    """
    Wrap flask's ``Config`` instance into compatible for ``setman`` library.
    """
    __slots__ = ('_config', )

    def __init__(self, config):
        self._config = config

    def __getattr__(self, name):
        return self._config[name]
