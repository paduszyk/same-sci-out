from django.contrib.contenttypes.fields import GenericRelation
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

from apps.outputs.contributions.models import Contribution
from base import models


class Element(models.Model):
    """A class to represent abstract Element objects."""

    class Meta:
        abstract = True

    title = models.TextField(_("tytuł"))
    contributions = GenericRelation(Contribution)

    def __str__(self):
        return "{} {}".format(
            f"{authors}:" if (authors := self.join_authors()) else "",
            self.get_truncated_title(),
        ).strip()

    def get_truncated_title(self, num_words=10):
        """Return the element's title truncated after a specified number of
        words."""
        return Truncator(self.title).words(num=num_words)

    def join_authors(self, sep=", ", num_explicit_authors=None):
        """Return a string listing aliases of the element's authors."""
        if (contributions := self.contributions.all()).exists():
            aliases = [contrib.author.alias for contrib in contributions]
            if num_explicit_authors and contributions.count() > num_explicit_authors:
                return _("%(first_author)s et al.") % {"first_author": aliases[0]}
            return sep.join(aliases)

    def by_employees_only(self):
        """Return a boolean indicating if the element is only by employees."""
        if (contributions := self.contributions.all()).exists():
            return all(contrib.by_employee() for contrib in contributions)
