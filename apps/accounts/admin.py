from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Permission, Role, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Profile",
            {
                "fields": (
                    "role",
                    "personnel",
                    "language",
                    "theme",
                    "photo",
                    "must_change_password",
                )
            },
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Profile", {"fields": ("email", "role", "language", "theme")}),
    )
    list_display = ("username", "email", "role", "is_active")
    list_filter = ("role", "is_active")


admin.site.register(Role)
admin.site.register(Permission)
