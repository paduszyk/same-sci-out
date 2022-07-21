from itertools import chain

from django.db import models
from django.db.models import *  # NOQA
from django.utils.translation import gettext_lazy as _

from .fields import YesNoAnswerField  # NOQA


class YesNoQuestionChoices(models.IntegerChoices):
    """ALternative choices for polar boolean fields if they are intend to be
    rendered as Yes/No selects instead of checkboxes."""

    YES = True, _("Tak")  # represented in DB as 1
    NO = False, _("Nie")  # represented in DB as 0


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

    def to_dict(self, *, fields=None, exclude=None):
        """Return a dict representation of the model instance."""
        if fields and exclude:
            raise ValueError(
                "Specifying both 'fields' or 'exclude' is prohibited. "
                "Use one of them while setting another as None."
            )

        opts = self.opts

        # Get all the fields
        all_fields = list(
            chain(
                opts.concrete_fields,
                opts.private_fields,
                opts.many_to_many,
            )
        )

        # Validate the names of the fields passed as `fields` or `exclude` parameter
        if fields or exclude:
            for field in fields or exclude:
                if field not in [field.name for field in all_fields]:
                    raise KeyError(
                        "Model {} has not a field '{}' given in '{}' parameter.".format(
                            opts.label, field, "fields" if fields else "exclude"
                        )
                    )

        # Apply filtering, collect & return the output dict
        if fields:
            all_fields = filter(lambda field: field.name in fields, all_fields)
        if exclude:
            all_fields = filter(lambda field: field.name not in exclude, all_fields)

        return {
            field.name: field.value_from_object(self)
            if not field.many_to_one
            else getattr(self, field.name)
            for field in all_fields
        }
