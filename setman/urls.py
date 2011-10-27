from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
        url(r'^edit_settings', 'setman.views.edit_settings',
            name='edit-settings'),
)
