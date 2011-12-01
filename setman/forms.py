from django import forms
from django.utils.datastructures import SortedDict

from setman import settings
from setman.utils import AVAILABLE_SETTINGS, is_settings_container


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
        self.fields = self.build_fields()

    def build_fields(self, settings=None, fields=None):
        """
        Build only fields from list of availabale settings.
        """
        fields = fields or SortedDict()
        settings = settings or AVAILABLE_SETTINGS

        for setting in settings:
            if is_settings_container(setting):
                fields = self.build_fields(setting, fields)
            else:
                field = setting.to_field()
                field.app_name = setting.app_name

                if setting.app_name:
                    name = '.'.join((setting.app_name, setting.name))
                else:
                    name = setting.name

                fields[name] = field

        return fields

    def save(self):
        """
        Save all settings to the database.
        """
        cd = self.cleaned_data

        for key, value in cd.items():
            if '.' in key:
                app_name, key = key.split('.', 1)
                setattr(getattr(settings, app_name), key, value)
            else:
                setattr(settings, key, value)

        settings.save()
