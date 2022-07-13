from base.options import admin
from base.options.decorators import as_html

from .models import Department, Faculty, University


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    """Admin options and functionalities for the University model."""

    list_display = ("name", "abbr")
    search_fields = ("name", "abbr")


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    """Admin options and functionalities for the Faculty model."""

    autocomplete_fields = ("ancestor",)

    list_display = ("name", "abbr", "university__name")
    search_fields = ("name", "abbr")

    @admin.display(
        description=University._meta.verbose_name,
        ordering="ancestor__name",
    )
    @as_html
    def university__name(self, obj):
        """Return the faculty's university name."""
        university = obj.university
        return university.get_admin_change_link(content=university.name)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin options and functionalities for the Department model."""

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
        faculty = obj.faculty
        return faculty.get_admin_change_link(content=faculty.name)

    @admin.display(
        description=University._meta.verbose_name,
        ordering="ancestor__ancestor__name",
    )
    @as_html
    def university__name(self, obj):
        """Return the departments's university name."""
        university = obj.faculty.university
        return university.get_admin_change_link(content=university.name)
