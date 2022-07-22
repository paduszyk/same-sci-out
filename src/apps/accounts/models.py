import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from base import models

from .constants import (
    SEX_CHOICES,
    SEX_DEFAULT,
    USER_ICON_PATH,
    USER_ICON_SIZE,
    USER_PHOTO_PATH,
    USER_PHOTO_SIZE,
)


def user_photo_path(instance, file_name):
    """Return a path to upload photos associated with the User objects."""
    _, file_ext = os.path.splitext(file_name)
    return os.path.join(USER_PHOTO_PATH, str(uuid.uuid4()) + file_ext)


def user_icon_path(instance, file_name):
    """Return a path to upload icons associated with the User objects."""
    _, file_ext = os.path.splitext(file_name)
    return os.path.join(USER_ICON_PATH, str(uuid.uuid4()) + file_ext)


class User(models.Model, AbstractUser):
    """A class to override the default User model from the
    `django.contrib.auth` app.

    The related models accounting for the groups and permission are
    taken directly from the base `django.contrib.auth` app.
    """

    sex = models.CharField(
        _("płeć"),
        max_length=max([len(sex) for sex in list(zip(*SEX_CHOICES))[0]]),
        choices=SEX_CHOICES,
        default=SEX_DEFAULT,
    )
    slug = models.SlugField(
        _("Slug"),
        blank=True,
        null=True,
        unique=True,
        default=None,
    )
    photo = models.ImageField(
        verbose_name=_("zdjęcie"),
        upload_to=user_photo_path,
        blank=True,
        help_text="%s<br>%s"
        % (
            _(
                "Przesłane zdjęcie zostanie wykadrowane obszarem największego "
                "i wyśrodkowanego kwadratu oraz przeskalowane do rozmiaru (%d x %d) px."
            )
            % USER_PHOTO_SIZE,
            _(
                "Dodatkowo na serwerze zostanie zapisana ikona o rozmiarze (%d x %d) "
                "px będąca pomniejszoną wersją zdjęcia (bez kadrowania)."
            )
            % USER_ICON_SIZE,
        ),
    )
    icon = models.ImageField(upload_to=user_icon_path, blank=True, editable=False)

    class Meta:
        verbose_name = _("użytkownik")
        verbose_name_plural = _("użytkownicy")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Update the help text of the `slug` field
        self._meta.get_field("slug").help_text = "%s<br>%s" % (
            _("Unikatowy tekstowy identyfikator w adresach URL."),
            _("Domyślnie, wartość pola „%s”.")
            % capfirst(self.opts.get_field("username").verbose_name),
        )

    def clean(self):
        super().clean()

        # Handle empty `slug` field
        if not self.slug:
            self.slug = self.username
