import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from base.options import models

# User photo and icon dirs and sizes

USER_PHOTO_DIR = os.path.join("accounts", "photos")
USER_PHOTO_SIZE = (512, 512)

USER_ICON_DIR = os.path.join("accounts", "icons")
USER_ICON_SIZE = (64, 64)


def photo_upload_path(instance, file_name):
    """Return a path to upload photos associated with User objects."""
    _, file_ext = os.path.splitext(file_name)
    return os.path.join(USER_PHOTO_DIR, str(uuid.uuid4()) + file_ext)


def icon_upload_path(instance, file_name):
    """Return a path to upload icons associated with User objects."""
    _, file_ext = os.path.splitext(file_name)
    return os.path.join(USER_ICON_DIR, str(uuid.uuid4()) + file_ext)


class User(AbstractUser, models.Model):
    """A class to represent User objects."""

    sex = models.CharField(
        _("płeć"),
        max_length=1,
        choices=[
            ("U", _("nie chcę podawać")),
            ("F", _("kobieta")),
            ("M", _("mężczyzna")),
        ],
        default="U",
    )
    slug = models.SlugField(_("Slug"), blank=True)
    photo = models.ImageField(
        verbose_name=_("zdjęcie"),
        upload_to=photo_upload_path,
        blank=True,
        null=True,
        help_text=_(
            "Przesłane zdjęcie zostanie wykadrowane obszarem największego "
            "i wyśrodkowanego kwadratu oraz przeskalowane do rozmiaru (%d x %d) px.<br>"
            "Dodatkowo na serwerze zostanie zapisana ikona o rozmiarze (%d x %d) px "
            "będąca pomniejszoną wersją zdjęcia (bez kadrowania)."
        )
        % (*USER_PHOTO_SIZE, *USER_ICON_SIZE),
    )
    icon = models.ImageField(
        verbose_name=_("ikona"),
        upload_to=icon_upload_path,
        blank=True,
        null=True,
        editable=False,
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

        # Update help text of the `slug` field
        self._meta.get_field("slug").help_text = _(
            "Identyfikator w adresach URL. Domyślnie, wartość pola %s."
        ) % capfirst(self._meta.get_field("username").verbose_name)

    def __str__(self):
        """Define how to print the object."""
        short_name = self.get_short_name()
        return "{} {}".format(
            short_name,
            f"({self.username})" if short_name else self.username,
        ).strip()

    def get_full_name(self):
        """Return the user's full name."""
        first_name = (
            "{} {}".format(
                first_names[0],
                " ".join([f"{first_name[:1]}." for first_name in first_names[1:]]),
            )
            if (first_names := self.first_name.split())
            else self.first_name
        )
        return f"{self.last_name} {first_name}".strip() or "-"

    def get_short_name(self):
        """Return the user's short name."""
        return "{} {}".format(
            self.last_name,
            " ".join([f"{first_name[:1]}." for first_name in self.first_name.split()]),
        ).strip()

    def clean(self):
        """Perform model-wide validation and updates."""
        # Handle empty `slug` field
        if not self.slug:
            self.slug = self.username

    @property
    def photo_url(self):
        """Return the user's photo URL."""
        if self.photo:
            return self.photo.url
        return static(self.get_static_path(f"photo-{self.sex}.png", model=True))

    @property
    def icon_url(self):
        """Return the user's icon URL."""
        if self.icon:
            return self.icon.url
        return static(self.get_static_path(f"icon-{self.sex}.png", model=True))
