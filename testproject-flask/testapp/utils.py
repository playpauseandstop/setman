from wtforms import fields, validators

from setman.utils.types import SetmanSetting


class IPAddressField(fields.TextField):

    validators = validators.IPAddress


class IPAddressSetting(SetmanSetting):

    type = 'ip'
    field_klass = IPAddressField
