from django.conf import settings as django_settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import simplejson

from setman import forms


__all__ = ('JSONField', )


class JSONField(models.TextField):
    """
    Model field that stores Python dict as JSON dump.

    You should set custom encoder class for dumps Python object to JSON data
    via ``encoder_cls`` keyword argument. By default, ``DjangoJSONEncoder``
    would be used.
    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.encoder_cls = kwargs.pop('encoder_cls', DjangoJSONEncoder)
        super(JSONField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(JSONField, self).contribute_to_class(cls, name)

        def get_json(model):
            return self.get_db_prep_value(getattr(model, self.attname))
        setattr(cls, 'get_%s_json' % self.name, get_json)

        def set_json(model, json):
            setattr(model, self.attname, self.to_python(json))
        setattr(cls, 'set_%s_json' % self.name, set_json)

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.JSONField}
        defaults.update(kwargs)
        field = super(JSONField, self).formfield(**defaults)

        if hasattr(field.widget, 'json_options') and \
           not 'cls' in field.widget.json_options:
            field.widget.json_options.update({'cls': self.encoder_cls})

        return field

    def get_default(self):
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        return super(JSONField, self).get_default()

    def get_prep_value(self, value):
        return simplejson.dumps(value, cls=self.encoder_cls)

    def to_python(self, value):
        if not isinstance(value, basestring):
            return value

        if value == '':
            return value

        try:
            return simplejson.loads(value,
                                    encoding=django_settings.DEFAULT_CHARSET)
        except ValueError, e:
            # If string could not parse as JSON it's means that it's Python
            # string saved to JSONField.
            return value
