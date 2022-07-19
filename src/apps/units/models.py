from types import MethodType

from django.utils.translation import gettext_lazy as _

from base import models


class AbstractUnit(models.Model):
    """A class to represent abstract Unit objects."""

    name = models.CharField(_("nazwa"), max_length=255)
    abbr = models.CharField(_("skrót"), max_length=255)

    ancestor = None  # to be overridden by the inheriting classes

    ANCESTOR_FIELD = "ancestor"
    FULL_NAME_SEP = ", "
    FULL_ABBR_SEP = "/"

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically add extra instance methods returning the object's ancestors
        # The methods are named following the pattern `get_ancestor`, where `ancestor`
        # is replaced by the `opts.model_name` value of the ancestor object.

        def _get_ancestor_method(ancestor):
            def func(self):
                return ancestor

            return func

        ancestors = self.ancestors(include_self=False)

        for ancestor in ancestors:
            setattr(
                self,
                f"get_{ancestor.opts.model_name}",
                MethodType(
                    _get_ancestor_method(ancestor),
                    self,
                ),
            )

    def __str__(self):
        return self.get_full_name()

    def ancestors(self, include_self=False):
        """A generator returning the unit's ancestors.

        Generator starts from the unit itself depending on the value of
        `include_self` attribute.
        """
        unit = (
            self
            if include_self
            else (self.ancestor if hasattr(self, self.ANCESTOR_FIELD) else None)
        )

        while unit is not None:
            yield unit
            unit = getattr(unit, self.ANCESTOR_FIELD, None)

    def get_full_name(self, sep=FULL_NAME_SEP, self_first=True):
        """Return the unit's full name.

        The full name includes the names of all the ancestors separated
        by `sep` string. Default order of the units forming the name
        (self unit goes first) can be reversed by setting `self_first`
        attribute to False.
        """
        names = [unit.name for unit in self.ancestors(include_self=True)]
        if not self_first:
            names.reverse()
        return sep.join(names)

    def get_full_abbr(self, sep=FULL_ABBR_SEP, self_first=True):
        """Return the unit's full abbreviation.

        The full name includes the abbreviations of all the ancestors
        separated by `sep` string. Default order of the units forming
        the abbreviation (self unit goes first) can be reversed by
        setting `self_first` attribute to False.
        """
        abbrs = [unit.abbr for unit in self.ancestors(include_self=True)]
        if not self_first:
            abbrs.reverse()
        return sep.join(abbrs)


class University(AbstractUnit):
    """A class to represent University objects."""

    class Meta:
        verbose_name = _("uczelnia")
        verbose_name_plural = _("uczelnie")


class Faculty(AbstractUnit):
    """A class to represent Faculty objects."""

    class Meta:
        verbose_name = _("wydział")
        verbose_name_plural = _("wydziały")

    ancestor = models.ForeignKey(
        to=University,
        on_delete=models.CASCADE,
        verbose_name=University.opts.verbose_name,
        related_name="faculties",
    )


class Department(AbstractUnit):
    """A class to represent Department objects."""

    class Meta:
        verbose_name = _("katedra")
        verbose_name_plural = _("katedry")

    ancestor = models.ForeignKey(
        to=Faculty,
        on_delete=models.CASCADE,
        verbose_name=Faculty.opts.verbose_name,
        related_name="departments",
    )
