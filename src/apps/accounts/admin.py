from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy

from base.options import admin

from .models import User


class MissingDataFilter(admin.SimpleListFilter):
    """Filtering the User objects by their complete/incomplete data."""

    parameter_name = "missing_data"
    title = _("brakujące dane")

    def lookups(self, request, model_admin):
        """Return the filter lookups."""
        return [(True, _("Tak")), (False, _("Nie"))]

    def queryset(self, request, queryset):
        """Update the changelist queryset based on the filter lookup selected."""
        if (value := self.value()) in ["True", "False"]:
            checked_fields, lookup = ["first_name", "last_name", "email"], Q()
            for field in checked_fields:
                lookup = lookup | Q(**{f"{field}__exact": ""})
            if value == "True":
                return queryset.filter(lookup)
            else:
                return queryset.exclude(lookup)


@admin.register(User)
class UserAdmin(admin.ModelAdmin, UserAdmin):
    """Admin options and functionalities for the User model."""

    class Media:
        css = {"all": ("admin/accounts/user/change_list_extras.css",)}

    fieldsets = (
        (None, {"fields": ("username", "password", "slug")}),
        (
            _("Informacje osobiste"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "sex",
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
    radio_fields = {"sex": admin.HORIZONTAL}

    list_display = (
        "username",
        "last_name",
        "first_name",
        "email",
        "last_login",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", MissingDataFilter)
    list_editable = ("is_active", "is_staff", "is_superuser")
    actions = ("activate_selected", "deactivate_selected")

    @admin.action(description=_("Aktywuj wybranych użytkowników"))
    def activate_selected(self, request, queryset):
        """Activate selected users."""
        queryset.filter(is_active=False).update(is_active=True)

        self.message_user(
            request,
            message=ngettext_lazy(
                "Aktywowano wybranego użytkownika.",
                "Aktywowano wybranych użytkowników.",
                queryset.count(),
            ),
            level=messages.SUCCESS,
        )

    @admin.action(description=_("Dezaktywuj wybranych użytkowników"))
    def deactivate_selected(self, request, queryset):
        """Deactivate selected users."""
        # Distinguish superusers from the regular users
        superusers = queryset.filter(is_superuser=True)

        if superusers.exists():
            if queryset.count() == superusers.count():
                # Only superusers selected
                self.message_user(
                    request,
                    message=format_html(
                        _("Nie można dezaktywować superużytkowników: %s.")
                        % (
                            ", ".join(
                                su.get_admin_change_link(content=su.username)
                                for su in superusers
                            ),
                        ),
                    ),
                    level=messages.ERROR,
                )
            else:
                queryset.filter(is_superuser=False).update(is_active=False)

                self.message_user(
                    request,
                    message=format_html(
                        _(
                            "Dezaktywowano %d z %d wybranych użytkowników. "
                            "Nie można dezaktywować superużytkowników: %s."
                        )
                        % (
                            queryset.count() - superusers.count(),
                            queryset.count(),
                            ", ".join(
                                su.get_admin_change_link(content=su.username)
                                for su in superusers
                            ),
                        ),
                    ),
                    level=messages.WARNING,
                )
        else:
            queryset.update(is_active=False)

            self.message_user(
                request,
                message=ngettext_lazy(
                    "Dezaktywowano wybranego użytkownika.",
                    "Dezaktywowano wybranych użytkowników.",
                    queryset.count(),
                ),
                level=messages.SUCCESS,
            )


# Grouping users is not relevant for the project, therefore the built-in
# django.contrib.auth.models.Group model is unregistered from the admin site.

admin.site.unregister(Group)
