from django.utils.translation import gettext_lazy as _

from base.options import models


class Unit(models.Model):
    """An abstract class to represent unit objects."""

    name = models.CharField(_("nazwa"), max_length=255)
    abbr = models.CharField(_("skrót"), max_length=255)

    ancestor = None

    class Meta:
        abstract = True

    def __str__(self):
        """Define how to print the object."""
        return self.get_full_name()

    def get_full_name(self, sep=", "):
        """Return the unit's full name including all the ancestors."""
        return sep.join(unit.name for unit in self.ancestors(include_self=True))

    def get_full_abbr(self, sep="/"):
        """Return the unit's full abbreviation including all the ancestors."""
        return sep.join(unit.abbr for unit in self.ancestors(include_self=True))

    def ancestors(self, include_self=False):
        """Generate ancestors."""
        unit = self if include_self else self.ancestor

        while unit is not None:
            yield unit
            unit = unit.ancestor


class University(Unit):
    """A class to represent University objects."""

    class Meta:
        verbose_name = _("uczelnia")
        verbose_name_plural = _("uczelnie")


class Faculty(Unit):
    """A class to represent Faculty objects."""

    class Meta:
        verbose_name = _("wydział")
        verbose_name_plural = _("wydziały")

    ancestor = models.ForeignKey(
        to=University,
        on_delete=models.CASCADE,
        verbose_name=University._meta.verbose_name_plural,
        related_name="faculties",
    )

    @property
    def university(self):
        """Return the object's ancestor, the university."""
        return self.ancestor


class Department(Unit):
    """A class to represent Department objects."""

    class Meta:
        verbose_name = _("katedra")
        verbose_name_plural = _("katedry")

    ancestor = models.ForeignKey(
        to=Faculty,
        on_delete=models.CASCADE,
        verbose_name=Faculty._meta.verbose_name,
        related_name="departments",
    )

    @property
    def faculty(self):
        """Return the object's ancestor, the faculty."""
        return self.ancestor

    @property
    def university(self):
        """Return the object's ancestor, the university."""
        return self.faculty.ancestor
