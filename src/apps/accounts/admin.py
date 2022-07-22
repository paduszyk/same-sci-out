from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _

from base import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin, UserAdmin):
    """A class to represent admin options for the User model."""

    fieldsets = (
        (None, {"fields": ("username", "password", "slug")}),
        (
            _("Dane osobowe"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "sex",
                    "photo",
                )
            },
        ),
        (
            _("Uprawnienia"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Ważne daty"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"fields": ("username", "password1", "password2")}),)


# Register extra models from `django.contrib.auth` app. This requires to unregister the
# Group model first, as it is registered by the default.

admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin, GroupAdmin):
    """A class to represent admin options form the Group model."""


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """A class to represent admin options form the Permission model."""
