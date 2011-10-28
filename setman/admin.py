from django.contrib import admin
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from setman.models import Settings
from setman.views import auth_permitted, edit
from setman.forms import SettingsForm

csrf_protect_m = method_decorator(csrf_protect)


class SettingsAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request):
        return auth_permitted(request.user)

    def has_delete_permission(self, request):
        return auth_permitted(request.user)

    def get_form(self, request, obj=None, **kwargs):
        return SettingsForm

    @csrf_protect_m
    def change_view(self, request, object_id, extra_context=None):
        return edit(request, is_admin=True)

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        return edit(request, is_admin=True)

admin.site.register(Settings, SettingsAdmin)
