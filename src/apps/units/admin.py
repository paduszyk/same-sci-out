from base import admin

from .models import Department, Faculty, University


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    """A class to represent admin options for the University model."""


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    """A class to represent admin options for the Faculty model."""


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """A class to represent admin options for the Department model."""
