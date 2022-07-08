from django.db import models
from django.db.models import *  # NOQA


class Model(models.Model):
    """Project-wide template to replace the built-in Django's base Model."""

    class Meta:
        abstract = True
