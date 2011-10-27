from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from setman.utils import AVAILABLE_SETTINGS


@login_required
def view_settings(request):
    """
    View Configuration Definition File for Test Project.

    Only logged in users can have access to this page.
    """
    filename = AVAILABLE_SETTINGS.path

    handler = open(filename, 'rb+')
    content = handler.read()
    handler.close()

    return render_to_response('view_settings.html',
                              {'content': content},
                              RequestContext(request))
