from django.db import NotSupportedError
from django.utils.translation import gettext_lazy as _

from . import models
from .constants import NO, YES


class YesNoAnswerField(models.Field):
    """A class to represent a field for general question answers."""

    description = "Answer for a general question."

    def __init__(self, *args, **kwargs):
        kwargs.update(
            {
                "max_length": 1,
                "choices": [(YES, _("Tak")), (NO, _("Nie"))],
            },
        )
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        """Override the base method."""
        name, path, args, kwargs = super().deconstruct()

        # Discard the `max_length` and `choices` options
        del kwargs["max_length"]
        del kwargs["choices"]

        return name, path, args, kwargs

    def db_type(self, connection):
        """Override the base method."""
        if connection.vendor == "mysql":
            return "VARCHAR(%d)" % self.max_length
        else:
            raise NotSupportedError(
                "Field {} not supported by database vendor '{}'.".format(
                    self.__class__.__name__,
                    connection.vendor,
                )
            )
