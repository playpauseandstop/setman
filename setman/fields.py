from django.conf import settings as django_settings
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import simplejson

from setman.utils import AVAILABLE_SETTINGS


__all__ = ('SettingsField', )


class SettingsField(models.TextField):
    """
    Model field that stores Python dict as JSON dump.

    Also on converting value from dump to Python field uses
    ``AVAILABLE_SETTINGS`` container to coerce stored values to real Python
    objects.

    You should set custom encoder class for dumps Python object to JSON data
    via ``encoder_cls`` keyword argument. By default, ``DjangoJSONEncoder``
    would be used.
    """
    __metaclass__ = models.SubfieldBase

    default = dict

    def __init__(self, *args, **kwargs):
        """
        Initialize settings field. Add support of ``encoder_cls`` keyword arg.
        """
        self.encoder_cls = kwargs.pop('encoder_cls', DjangoJSONEncoder)
        super(SettingsField, self).__init__(*args, **kwargs)

    def clean(self, value, instance):
        """
        Run validation for each setting value.
        """
        data = {} if not value else value

        for name, value in data.items():
            if not hasattr(AVAILABLE_SETTINGS, name):
                continue

            setting = getattr(AVAILABLE_SETTINGS, name)
            data[name] = setting.to_field(initial=value).clean(value)

        return data

    def contribute_to_class(self, cls, name):
        super(SettingsField, self).contribute_to_class(cls, name)

        def get_json(model):
            return self.get_db_prep_value(getattr(model, self.attname))
        setattr(cls, 'get_%s_json' % self.name, get_json)

        def set_json(model, json):
            setattr(model, self.attname, self.to_python(json))
        setattr(cls, 'set_%s_json' % self.name, set_json)

    def get_default(self):
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        return super(SettingsField, self).get_default()

    def get_prep_value(self, value):
        return simplejson.dumps(value, cls=self.encoder_cls)

    def to_python(self, value):
        if not isinstance(value, basestring):
            return value

        if value == '':
            return value

        try:
            data = simplejson.loads(value,
                                    encoding=django_settings.DEFAULT_CHARSET)
        except ValueError:
            # If string could not parse as JSON it's means that it's Python
            # string saved to SettingsField.
            return value

        for key, value in data.items():
            if hasattr(AVAILABLE_SETTINGS, key):
                setting = getattr(AVAILABLE_SETTINGS, key)
                data[key] = setting.to_python(value)

        return data


# Add suport of SettingsField for South
def add_south_introspector_rules():
    rules = [((SettingsField, ), [], {})]
    add_introspection_rules(rules, ['^setman\.fields'])


try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_south_introspector_rules()
