from django import forms

from setman.utils import Setting


class IPAddressSetting(Setting):

    type = 'ip'
    field_klass = forms.IPAddressField
