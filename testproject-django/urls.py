from django.conf import settings
from django.conf.urls.defaults import include, patterns
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template


admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', login_required(direct_to_template), {'template': 'home.html'},
     'home'),

    (r'^odesk_auth/', include('django_odesk.auth.urls')),

    (r'^accounts/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'registration/logout.html'}),
    (r'^accounts/', include('django.contrib.auth.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^setman/', include('setman.frameworks.django_setman.urls')),
    (r'^test/', include('testapp.urls')),
)

if settings.SERVE_STATIC_FILES:
    urlpatterns += patterns('django.views.static',
        ('^favicon.ico', 'serve', {'document_root': settings.MEDIA_ROOT,
                                   'path': 'favicon.ico'}),
        ('^%s/(?P<path>.*)$' % settings.MEDIA_URL.strip('/'), 'serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
