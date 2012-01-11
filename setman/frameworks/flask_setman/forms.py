try:
    from wtforms.ext.csrf.form import SecureForm as Form
except ImportError:
    from wtforms.form import Form

from setman import settings


__all__ = ('SettingsForm', )


class SettingsForm(Form):
    """
    Simple settings form, which would be dynamically extended by available
    settings later.
    """
    def save(self):
        """
        Add support for saving form data as settings values.
        """
        settings._framework.save_form_fields(self.data)


fields = settings._framework.build_form_fields()

for name, field in fields.iteritems():
    setattr(SettingsForm, name, field)
