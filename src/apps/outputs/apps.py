from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OutputsConfig(AppConfig):
    """A class to represent the `outputs` app configuration."""

    default_auto_field = "django.db.models.BigAutoField"

    name = "apps.outputs"
    verbose_name = _("dorobek")
