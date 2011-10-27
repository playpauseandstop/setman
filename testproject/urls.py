from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    url(r'^$', 'core.views.homepage', name='homepage'),
    url(r'^setman/', include('setman.urls')),
)
