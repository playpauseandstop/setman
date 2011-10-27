from django import forms
from setman.utils import AVAILABLE_SETTINGS


class SettingsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        from setman import settings
        super(SettingsForm, self).__init__(*args, **kwargs)

        for setting in AVAILABLE_SETTINGS:
            self.fields[setting.name] = setting.to_field()

    def save(self):
        from setman import settings
        for value in self.cleaned_data:
            setattr(settings, value, self.cleaned_data[value])
        settings.save()
