from django.views.generic.simple import direct_to_template

from setman.forms import SettingsForm


def edit_settings(request):
    """
    Edit Settings Page provide basic UI
    for changing Settings.
    """
    form = SettingsForm(request.POST or None)
    if form.is_valid():
        form.save()

    return direct_to_template(request, 'edit_settings.html', {'form': form})
