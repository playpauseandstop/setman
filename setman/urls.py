from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('setman.views',
    url(r'^$', 'edit', name='setman_edit'),
    url(r'^revert/$', 'revert', name='setman_revert'),
)
