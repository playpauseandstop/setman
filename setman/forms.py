from django import forms

from setman import settings
from setman.utils import AVAILABLE_SETTINGS


class SettingsForm(forms.Form):
    """
    Edit Settings form.
    """
    def __init__(self, *args, **kwargs):
        """
        Read all available settings from configuration definition file and
        add field for each setting to the form.
        """
        super(SettingsForm, self).__init__(*args, **kwargs)

        for setting in AVAILABLE_SETTINGS:
            self.fields[setting.name] = setting.to_field()

    def save(self):
        """
        Save all settings to the database.
        """
        cd = self.cleaned_data

        for key, value in cd.items():
            setattr(settings, key, value)

        settings.save()
