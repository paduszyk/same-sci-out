from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    """A class to represent the `accounts` app configuration."""

    default_auto_field = "django.db.models.BigAutoField"

    name = "apps.accounts"
    verbose_name = _("konta")
