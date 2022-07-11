from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from base.options import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin, UserAdmin):
    """Admin options and functionalities for the User model."""

    list_display = (
        "username",
        "last_name",
        "first_name",
        "email",
        "last_login",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")


# Grouping users is not relevant for the project, therefore the built-in
# django.contrib.auth.models.Group model is unregistered from the admin site.

admin.site.unregister(Group)
