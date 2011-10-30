from django.contrib import admin
from django.contrib.admin.options import csrf_protect_m

from setman.models import Settings
from setman.views import edit
from setman.utils import auth_permitted


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
        return auth_permitted(request.user)

    def has_delete_permission(self, request):
        """
        Do not show "Delete" link in admin panel for "Settings" models.
        """
        return auth_permitted(request.user)


admin.site.register(Settings, SettingsAdmin)
