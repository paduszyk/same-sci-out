from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EmployeesConfig(AppConfig):
    """Class representing the `employees` app and its configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.employees"
    verbose_name = _("Kadra")
