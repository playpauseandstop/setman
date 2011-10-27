from random import randint

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from setman.forms import SettingsForm


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
    if request.method == 'POST':
        form = SettingsForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, _('Settings have been updated.'))

            return redirect('%s?%d' % (request.path, randint(1000, 9999)))
    else:
        form = SettingsForm()

    return render_to_response('setman/edit.html',
                              {'form': form},
                              RequestContext(request))
