from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    """Class representing the `accounts` app and its configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = _("Konta")

    def ready(self):
        """Run this code when the Django starts."""
        from . import signals  # NOQA
