from random import randint

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.utils.translation import ugettext as _

from setman import settings
from setman.forms import SettingsForm
from setman.utils import AVAILABLE_SETTINGS


@login_required
def edit(request):
    """
    Edit Settings page.

    By default only logged in superusers can have access to this page. But you
    can customize things, by setup ``SETMAN_AUTH_PERMITTED`` option.

    For example, if you need to permit staff users to edit settings too, you
    need to specify::

        SETMAN_AUTH_PERMITTED = lambda u: u.is_staff

    in your project settings module.

    Also, you can check necessary profile role there as well as::

        SETMAN_AUTH_PERMITTED = lambda u: u.profile.role == 'project_manager'

    But also, don't forget that only **logged** in users can access this page.
    Not guest users able to edit custom project settings in any way.
    """
    permitted = getattr(django_settings, 'SETMAN_AUTH_PERMITTED', None)

    if not permitted:
        permitted = lambda user: user.is_superuser

    if not permitted(request.user):
        return render(request,
                      'setman/edit.html',
                      {'auth_forbidden': True},
                      status=403)

    if request.method == 'POST':
        form = SettingsForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request, _('Settings have been succesfully updated.')
            )

            return redirect('%s?%d' % (request.path, randint(1000, 9999)))
    else:
        form = SettingsForm()

    return render(request, 'setman/edit.html', {'form': form})


@login_required
def revert(request):
    """
    Revert settings to default values.

    This view uses same permission rules as "Edit Settings" view.
    """
    permitted = getattr(django_settings, 'SETMAN_AUTH_PERMITTED', None)
    redirect_to = reverse('setman_edit')

    if not permitted:
        permitted = lambda user: user.is_superuser

    if not permitted(request.user):
        return render(request,
                      'setman/edit.html',
                      {'auth_forbidden': True},
                      status=403)

    for setting in AVAILABLE_SETTINGS:
        setattr(settings, setting.name, setting.default)

    settings.save()
    messages.success(
        request, _('Settings have been reverted to default values.')
    )

    return redirect('%s?%d' % (redirect_to, randint(1000, 9999)))

