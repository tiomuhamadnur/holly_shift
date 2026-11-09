from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("at", "user", "action", "entity", "entity_id", "ip")
    list_filter = ("action", "entity")
    search_fields = ("entity", "entity_id", "user__username")
    readonly_fields = ("at", "user", "ip", "action", "entity", "entity_id", "before", "after")
    date_hierarchy = "at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
