from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from base import models


class User(models.Model, AbstractUser):
    """A class to override the default User model from the
    `django.contrib.auth` app.

    The related models accounting for the groups and permission are
    taken directly from the base `django.contrib.auth` app.
    """

    class Meta:
        verbose_name = _("użytkownik")
        verbose_name_plural = _("użytkownicy")
