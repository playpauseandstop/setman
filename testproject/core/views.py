import os

from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from setman.utils import AVAILABLE_SETTINGS


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
    filename = AVAILABLE_SETTINGS.path

    handler = open(filename, 'rb')
    content = handler.read()
    handler.close()

    return render(request, 'view_settings.html', {'content': content})
