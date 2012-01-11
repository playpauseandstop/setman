from wtforms import fields, validators

from setman.utils.types import SetmanSetting


class IPAddressField(fields.TextField):

    def __init__(self, **kwargs):
        if not 'validators' in kwargs:
            kwargs['validators'] = []
        kwargs['validators'].append(validators.IPAddress())

        super(IPAddressField, self).__init__(**kwargs)


class IPAddressSetting(SetmanSetting):

    type = 'ip'
    field_klass = IPAddressField
