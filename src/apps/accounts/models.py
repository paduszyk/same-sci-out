from django.contrib.auth.models import AbstractUser
from django.utils.text import capfirst
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
    slug = models.SlugField(_("Slug"), blank=True)

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

        # Update help text of the `slug` field
        self._meta.get_field("slug").help_text = _(
            "Identyfikator w adresach URL. Domyślnie, wartość pola %s."
        ) % capfirst(self._meta.get_field("username").verbose_name)

    def clean(self):
        """Perform model-wide validation and updates."""
        # Handle empty `slug` field
        if not self.slug:
            self.slug = self.username
