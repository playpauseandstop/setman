from django import forms
from django.utils.translation import ugettext_lazy as _


__all__ = ('SandboxForm', )


class SandboxForm(forms.Form):
    """
    Simple form form "Sandbox" page.
    """
    FORBIDDEN_SETTINGS = (
        'DATABASES', 'ODESK_PRIVATE_KEY', 'ODESK_PUBLIC_KEY', 'SECRET_KEY'
    )

    name = forms.CharField(label=_('Name'), required=True,
        help_text=_('Enter name of available setting, press Enter - get ' \
                    'setting value.'),
        widget=forms.TextInput(attrs={'size': 50}))

    def clean_name(self):
        name = self.cleaned_data['name']

        if name in self.FORBIDDEN_SETTINGS:
            raise forms.ValidationError(_(
                'The value for this setting is forbidden.'
            ))

        return name
