from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from base import models

from .constants import SEX_CHOICES, SEX_DEFAULT


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

    class Meta:
        verbose_name = _("użytkownik")
        verbose_name_plural = _("użytkownicy")
