from base import admin

from .forms import EmployeeAdminChangeForm, PositionAdminChangeForm
from .models import (
    AcademicDegree,
    Discipline,
    Employee,
    EmployeeGroup,
    EmployeeStatus,
    Employment,
    Position,
)


@admin.register(EmployeeStatus)
class EmployeeStatusAdmin(admin.ModelAdmin):
    """A class to represent admin options for the EmployeeStatus model."""


@admin.register(EmployeeGroup)
class EmployeeGroupAdmin(admin.ModelAdmin):
    """A class to represent admin options for the EmployeeGroup model."""


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """A class to represent admin options for the Position model."""

    form = PositionAdminChangeForm


@admin.register(AcademicDegree)
class AcademicDegreeAdmin(admin.ModelAdmin):
    """A class to represent admin options for the AcademicDegree model."""


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    """A class to represent admin options for the Discipline model."""


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """A class to represent admin options for the Employee model."""

    form = EmployeeAdminChangeForm


@admin.register(Employment)
class EmploymentAdmin(admin.ModelAdmin):
    """A class to represent admin options for the Employment model."""
