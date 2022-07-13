from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.html import format_html
from django.utils.text import capfirst, format_lazy
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


class HasPhotoFilter(admin.SimpleListFilter):
    """Filtering the User objects by their photos."""

    parameter_name = "has_photo"
    title = _("ze zdjęciem")

    def lookups(self, request, model_admin):
        """Return the filter lookups."""
        return [(True, _("Tak")), (False, _("Nie"))]

    def queryset(self, request, queryset):
        """Update the changelist queryset based on the filter lookup selected."""
        if (value := self.value()) in ["True", "False"]:
            if value == "True":
                return queryset.exclude(photo__exact="")
            else:
                return queryset.filter(photo__exact="")


@admin.register(User)
class UserAdmin(admin.ModelAdmin, UserAdmin):
    """Admin options and functionalities for the User model."""

    class Media:
        css = {
            "all": (
                User.get_static_path(
                    "change_list.css",
                    model=True,
                    admin=True,
                ),
            )
        }

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
    radio_fields = {"sex": admin.HORIZONTAL}

    list_display = (
        "username",
        "full_name",
        "photo_display",
        "last_login",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        MissingDataFilter,
        HasPhotoFilter,
    )
    list_editable = ("is_active", "is_staff", "is_superuser")
    actions = ("activate_selected", "deactivate_selected", "delete_photo_of_selected")

    @admin.display(description=_("Nazwisko i imiona"))
    def full_name(self, obj):
        """Return the user's full name."""
        return obj.get_full_name()

    @admin.display(description=capfirst(User._meta.get_field("photo").verbose_name))
    def photo_display(self, obj):
        """Return HTML code displaying the user icon."""
        return format_html(
            format_lazy(
                '<a href="{}" target="_blank" title="{}"><img src="{}" alt="{}"></a>',
                obj.photo_url,
                _("Przejdź do zdjęcia"),
                obj.icon_url,
                _("Zdjęcie profilowe użytkownika: %s") % obj,
            )
        )

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

    @admin.action(description=_("Usuń zdjęcia wybranych użytkowników"))
    def delete_photo_of_selected(self, request, queryset):
        """Delete photo files of the selected users."""
        users_with_photo = queryset.exclude(photo__exact="")

        for user in users_with_photo:
            user.photo = None  # icon is removed automatically by the post_save signal
            user.save()

        if users_with_photo.exists():
            self.message_user(
                request,
                message=_("Usunięto zdjęcia wybranych użytkowników."),
                level=messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                message=_("Wybrani użytkownicy nie mają przypisanego zdjęcia."),
                level=messages.WARNING,
            )


# Grouping users is not relevant for the project, therefore the built-in
# django.contrib.auth.models.Group model is unregistered from the admin site.

admin.site.unregister(Group)
