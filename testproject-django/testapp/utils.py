from django import forms

from setman.utils.types import SetmanSetting


class IPAddressSetting(SetmanSetting):

    type = 'ip'
    field_klass = forms.IPAddressField
