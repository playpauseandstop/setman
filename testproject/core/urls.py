from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('testproject.core.views',
    url(r'view-settings/$', 'view_settings', name='view_settings'),
)
