import re

from decimal import Decimal

from setman.exceptions import ValidationError
from setman.utils import importlib, logger
from setman.utils.common import force_bool, load_from_path
from setman.utils.validators import decimal_places_validator, \
    max_digits_validator, max_length_validator, max_value_validator, \
    min_length_validator, min_value_validator, regex_validator


__all__ = ('SetmanSetting', 'BooleanSetting', 'ChoiceSetting',
           'DecimalSetting', 'FloatSetting', 'IntSetting', 'StringSetting')


class SetmanSetting(object):
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
    help_text = None
    field_args = ('label', 'help_text', 'initial', 'required', 'validators')
    field_klass = None
    field_kwargs = {}
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
    def builtin_validators(self):
        """
        List of builtin validators to use cause of setting attributes.
        """
        return None

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

    def get_field_args(self):
        """
        Return list of all available setting field keyword arguments keys.
        """
        return self.field_args

    def get_field_kwargs(self):
        """
        Return dict of all available setting field keyword arguments.
        """
        return self.field_kwargs

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

    def validate(self, value):
        """
        Run all available validators for current setting and raise
        ``ValidationError`` if some checkin ended with error.

        As result return validated value.
        """
        has_value = bool(value)
        value = self.to_python(value)

        if not self.required and not value:
            return value

        if value is None:
            if has_value:
                raise ValidationError('Enter a valid value.')

            if self.required:
                raise ValidationError('This setting is required.')

            return value

        for validator in self.validators:
            value = validator(value)

        return value

    @property
    def validators(self):
        """
        Lazy loaded validators.
        """
        cache_key = '_validators_cache'
        if not hasattr(self, cache_key):
            setattr(self, cache_key, self._parse_validators(self._validators))

        builtin_validators = list(self.builtin_validators or [])
        loaded_validators = getattr(self, cache_key)

        return builtin_validators + loaded_validators

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


class BooleanSetting(SetmanSetting):
    """
    Boolean setting.
    """
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


class ChoiceSetting(SetmanSetting):
    """
    Choice setting.
    """
    choices = None
    field_args = SetmanSetting.field_args + ('choices', )
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

        """
        # Start parsing with internal choices
        if not ',' in value and '.' in value:
            # Choices tuple should be last part of value
            path, attr = value.rsplit('.', 1)

            # Load choices from module
            try:
                module = importlib.import_module(path)
            except ImportError:
                # Or from module class
                try:
                    module = load_from_path(path)
                except (AttributeError, ImportError):
                    logger.exception('Cannot load choices from %r path',
                                     value)
                    return ()

            # Try to get choices attr in module
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


class DecimalSetting(SetmanSetting):
    """
    Decimal setting.
    """
    decimal_places = None
    field_args = SetmanSetting.field_args + ('decimal_places', 'max_digits',
                                             'max_value', 'min_value')
    max_digits = None
    max_value = None
    min_value = None
    type = 'decimal'

    @property
    def builtin_validators(self):
        validators = []

        if self.decimal_places is not None:
            validators.append(decimal_places_validator(self.decimal_places))

        if self.max_digits is not None:
            validators.append(max_digits_validator(self.max_digits))

        if self.max_value is not None:
            validators.append(max_value_validator(self.max_value))

        if self.min_value is not None:
            validators.append(min_value_validator(self.min_value))

        return validators

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


class IntSetting(SetmanSetting):
    """
    Integer setting.
    """
    field_args = SetmanSetting.field_args + ('max_value', 'min_value')
    max_value = None
    min_value = None
    type = 'int'

    @property
    def builtin_validators(self):
        validators = []

        if self.max_value is not None:
            validators.append(max_value_validator(self.max_value))

        if self.min_value is not None:
            validators.append(min_value_validator(self.min_value))

        return validators

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
    type = 'float'

    def to_python(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


class StringSetting(SetmanSetting):
    """
    String setting.
    """
    max_length = None
    min_length = None
    regex = None
    type = 'string'

    @property
    def builtin_validators(self):
        validators = []

        if self.max_length is not None:
            validators.append(max_length_validator(self.max_length))

        if self.min_length is not None:
            validators.append(min_length_validator(self.min_length))

        if self.regex is not None:
            validators.append(regex_validator(self.regex))

        return validators

    def get_field_args(self):
        """
        Use ``RegexField`` for string setting if ``regex`` was filled in
        configuration definition file.
        """
        if self.regex:
            if not 'regex' in self.field_args:
                return self.field_args + ('regex', )
        return super(StringSetting, self).get_field_args()

    def update(self, **kwargs):
        super(StringSetting, self).update(**kwargs)

        int_setting = IntSetting()
        self.max_length = int_setting.to_python(self.max_length)
        self.min_length = int_setting.to_python(self.min_length)
