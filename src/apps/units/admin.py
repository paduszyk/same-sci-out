from django.utils.translation import gettext_lazy as _

from base.options import admin
from base.options.decorators import as_html

from .models import Department, Faculty, University


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    """Admin options and functionalities for the University model."""

    class FacultyInline(admin.TabularInline):
        model = Faculty
        extra = 1

    inlines = (FacultyInline,)

    list_display = ("name", "abbr", "faculty__list")
    search_fields = ("name", "abbr")

    @admin.display(description=Faculty._meta.verbose_name_plural)
    @as_html
    def faculty__list(self, obj):
        """Return a list of faculties related to the object."""
        if (faculties := obj.faculties.all()).exists():
            return "<br>".join(
                faculty.get_admin_change_link(content="name") for faculty in faculties
            )
        else:
            return "-"


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    """Admin options and functionalities for the Faculty model."""

    class DepartmentInline(admin.TabularInline):
        model = Department
        extra = 1

    fieldsets = (
        (None, {"fields": ("name", "abbr")}),
        (_("Jednostka nadrzędna"), {"fields": ("ancestor",)}),
    )
    autocomplete_fields = ("ancestor",)
    inlines = (DepartmentInline,)

    list_display = ("name", "abbr", "university__name", "department__list")
    search_fields = ("name", "abbr")

    @admin.display(
        description=University._meta.verbose_name,
        ordering="ancestor__name",
    )
    @as_html
    def university__name(self, obj):
        """Return the faculty's university name."""
        return obj.university.get_admin_change_link(content="name")

    @admin.display(description=Department._meta.verbose_name_plural)
    @as_html
    def department__list(self, obj):
        """Return a list of departments related to the object."""
        if (departments := obj.departments.all()).exists():
            return "<br>".join(
                department.get_admin_change_link(content="name")
                for department in departments
            )
        return "-"


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin options and functionalities for the Department model."""

    fieldsets = (
        (None, {"fields": ("name", "abbr")}),
        (_("Jednostka nadrzędna"), {"fields": ("ancestor",)}),
    )
    autocomplete_fields = ("ancestor",)

    list_display = ("name", "abbr", "faculty__name", "university__name")
    search_fields = ("name", "abbr")

    @admin.display(
        description=Faculty._meta.verbose_name,
        ordering="ancestor__name",
    )
    @as_html
    def faculty__name(self, obj):
        """Return the departments's faculty name."""
        return obj.faculty.get_admin_change_link(content="name")

    @admin.display(
        description=University._meta.verbose_name,
        ordering="ancestor__ancestor__name",
    )
    @as_html
    def university__name(self, obj):
        """Return the departments's university name."""
        return obj.faculty.university.get_admin_change_link(content="name")
