from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from base.options import models


class User(AbstractUser, models.Model):
    """A class to represent User objects."""

    def __init__(self, *args, **kwargs):
        """Overwrite the base constructor."""
        super().__init__(*args, **kwargs)

        # Update the verbose names for some fields
        self._meta.get_field("first_name").verbose_name = _("Imiona")
        self._meta.get_field("email").verbose_name = _("E-mail")
        self._meta.get_field("is_staff").verbose_name = _("Administrator")
        self._meta.get_field("is_superuser").verbose_name = _("Superużytkownik")
