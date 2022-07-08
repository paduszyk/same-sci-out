from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ExtrasConfig(AppConfig):
    """Class representing the `extras` app and its configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.extras"
    verbose_name = _("Dodatki")
