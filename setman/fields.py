from django.conf import settings as django_settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import simplejson

from setman import forms
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

    def __init__(self, *args, **kwargs):
        self.encoder_cls = kwargs.pop('encoder_cls', DjangoJSONEncoder)
        super(SettingsField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(SettingsField, self).contribute_to_class(cls, name)

        def get_json(model):
            return self.get_db_prep_value(getattr(model, self.attname))
        setattr(cls, 'get_%s_json' % self.name, get_json)

        def set_json(model, json):
            setattr(model, self.attname, self.to_python(json))
        setattr(cls, 'set_%s_json' % self.name, set_json)

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.SettingsField}
        defaults.update(kwargs)
        field = super(SettingsField, self).formfield(**defaults)

        if hasattr(field.widget, 'json_options') and \
           not 'cls' in field.widget.json_options:
            field.widget.json_options.update({'cls': self.encoder_cls})

        return field

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
        except ValueError, e:
            # If string could not parse as JSON it's means that it's Python
            # string saved to SettingsField.
            return value

        for key, value in data.items():
            if hasattr(AVAILABLE_SETTINGS, key):
                setting = getattr(AVAILABLE_SETTINGS, key)
                data[key] = setting.to_python(value)

        return data
