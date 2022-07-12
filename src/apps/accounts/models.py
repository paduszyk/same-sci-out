from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from base.options import models


class User(AbstractUser, models.Model):
    """A class to represent User objects."""

    sex = models.CharField(
        _("płeć"),
        max_length=1,
        choices=[
            ("", _("nie chcę podawać")),
            ("F", _("kobieta")),
            ("M", _("mężczyzna")),
        ],
        blank=True,
    )

    def __init__(self, *args, **kwargs):
        """Overwrite the base constructor."""
        super().__init__(*args, **kwargs)

        # Update the verbose names for some fields
        for old_name, new_name in {
            "username": _("Nazwa"),
            "first_name": _("Imiona"),
            "email": _("E-mail"),
            "is_staff": _("Administrator"),
            "is_superuser": _("Superużytkownik"),
        }.items():
            self._meta.get_field(old_name).verbose_name = new_name
