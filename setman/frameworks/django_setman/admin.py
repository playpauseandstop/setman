from django.contrib import admin
from django.contrib.admin.options import csrf_protect_m

from setman.frameworks.django_setman.models import Settings
from setman.frameworks.django_setman.views import edit
from setman.utils.auth import auth_permitted


class SettingsAdmin(admin.ModelAdmin):
    """
    Customize how Django admin shows Settings change and change list views.
    """
    app_label = Settings._meta.app_label.title()

    @csrf_protect_m
    def change_view(self, request, object_id, extra_context=None):
        """
        Show "Edit Settings" page instead of Django's default page for
        changing Settings model.
        """
        return edit(request, 'setman/admin/edit.html', self.app_label)

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        """
        Show "Edit Settings" page instead of Django's default page for
        showing models in "Settings Manager" app.
        """
        return edit(request, 'setman/admin/edit.html', self.app_label)

    def get_urls(self):
        """
        Add support of "Revert" to Django admin panel. This needs to use all
        functional of "Edit Settings" page without including ``setman.urls``
        patterns into root URLConf module.
        """
        from django.conf.urls.defaults import patterns, url

        urlpatterns = patterns('setman.frameworks.django_setman.views',
            url(r'^revert/$', 'revert', name='django_setman_settings_revert'),
        )
        urlpatterns += super(SettingsAdmin, self).get_urls()

        return urlpatterns

    def has_add_permission(self, request):
        """
        Do not show "Add" link in admin panel for "Settings" line in
        "Settings Manager" app.
        """
        return False

    def has_change_permission(self, request):
        """
        Do not show "Change" link in admin panel for "Settings" line in
        "Settings Manager" app.
        """
        return auth_permitted(request)

    def has_delete_permission(self, request):
        """
        Do not show "Delete" link in admin panel for "Settings" models.
        """
        return auth_permitted(request)


admin.site.register(Settings, SettingsAdmin)
