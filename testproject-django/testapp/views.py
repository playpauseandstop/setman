import os

from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.datastructures import SortedDict

from setman import settings
from setman.helpers import get_config
from setman.utils.parsing import is_settings_container

from testapp.forms import SandboxForm


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
def sandbox(request):
    """
    Simple sandbox.

    Only logged in users can have access to this page.
    """
    def get_django_names():
        names = []

        for name in dir(django_settings):
            if name.startswith('_') or name in ('configure', 'configured'):
                continue
            if name in SandboxForm.FORBIDDEN_SETTINGS:
                continue
            names.append(name)

        return tuple(names)

    def get_setman_names(available_settings=None):
        available_settings = available_settings or settings.available_settings
        data = []

        for setting in available_settings:
            if is_settings_container(setting):
                data.extend(get_setman_names(setting))
            else:
                if setting.app_name:
                    name = '.'.join((setting.app_name, setting.name))
                else:
                    name = setting.name
                data.append(name)

        return data

    context = {'django_names': get_django_names(),
               'setman_names': get_setman_names()}

    if request.method == 'POST':
        form = SandboxForm(request.POST)

        if form.is_valid():
            has_traceback = False
            name = form.cleaned_data['name']

            try:
                value = get_config(name)
            except:
                has_traceback = True
                value = traceback.format_exc()

            context.update({'has_traceback': has_traceback,
                            'has_value': True,
                            'value': value})
    else:
        form = SandboxForm()

    context.update({'form': form})
    return render(request, 'sandbox.html', context)


@login_required
def view_settings(request):
    """
    View Configuration Definition File for Test Project.

    Only logged in users can have access to this page.
    """
    path = settings.available_settings.path

    handler = open(path, 'rb')
    project_settings_content = handler.read()
    handler.close()

    apps_settings_contents = SortedDict()

    for setting in settings.available_settings:
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
