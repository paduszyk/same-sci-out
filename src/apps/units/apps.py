from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UnitsConfig(AppConfig):
    """Class representing the `units` app and its configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.units"
    verbose_name = _("Jednostki")
