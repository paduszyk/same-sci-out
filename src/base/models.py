from django.db import models
from django.db.models import *  # NOQA


class Model(models.Model):
    """A class to override `django.db.models.Model` class, hence to provide
    project-wide customizations of the default models."""

    class Meta:
        abstract = True

    @classmethod
    @property
    def opts(cls):
        """Return meta options object for the model class."""
        return cls._meta
