import os

from django.conf import settings as django_settings
from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.static import serve


root_dirname = os.path.normpath(os.path.join(django_settings.DIRNAME, '..'))
docs_dirname = os.path.join(root_dirname, 'docs', '_build', 'html')

urlpatterns = patterns('testproject.core.views',
    url(r'docs/$', 'docs', name='docs'),
    ('^docs/(?P<path>.*)$', login_required(serve),
     {'document_root': docs_dirname}, 'docs_browser'),
    url(r'view-settings/$', 'view_settings', name='view_settings'),
)
