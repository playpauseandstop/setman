import os

from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.datastructures import SortedDict

from setman.utils import AVAILABLE_SETTINGS, is_settings_container


@login_required
def docs(request):
    """
    Documentation page.

    Only logged in users can have access to this page.
    """
    dirname = os.path.normpath(os.path.join(django_settings.DIRNAME, '..'))
    filename = os.path.join(dirname, 'docs', '_build', 'html', 'index.html')

    if os.path.isfile(filename):
        return redirect('docs_browser', path='index.html')

    return render(request, 'docs.html', {'dirname': dirname})


@login_required
def view_settings(request):
    """
    View Configuration Definition File for Test Project.

    Only logged in users can have access to this page.
    """
    handler = open(AVAILABLE_SETTINGS.path, 'rb')
    project_settings_content = handler.read()
    handler.close()

    apps_settings_contents = SortedDict()

    for setting in AVAILABLE_SETTINGS:
        if is_settings_container(setting):
            handler = open(setting.path, 'rb')
            apps_settings_contents[setting.app_name] = handler.read()
            handler.close()

    filename = getattr(django_settings, 'SETMAN_DEFAULT_VALUES_FILE', None)

    if filename:
        handler = open(filename, 'rb')
        default_values_content = handler.read()
        handler.close()
    else:
        default_values_content = None

    context = {'apps_settings_contents': apps_settings_contents,
               'default_values_content': default_values_content,
               'project_settings_content': project_settings_content}
    return render(request, 'view_settings.html', context)
