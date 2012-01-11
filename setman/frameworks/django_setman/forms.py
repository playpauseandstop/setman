from django import forms
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_unicode

from setman import settings


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
        self.fields = settings._framework.build_form_fields()

    def save(self):
        """
        Save all settings to the database.
        """
        settings._framework.save_form_fields(self.cleaned_data)
