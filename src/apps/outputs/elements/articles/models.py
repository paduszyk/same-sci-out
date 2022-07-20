from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from base import models
from base import utils as base_utils

from ..models.base import Element
from . import constants


class Publisher(models.Model):
    """A class to represent Publisher objects."""

    class KindChoices(models.TextChoices):
        """Choices enumeration for the `kind` field."""

        FOREIGN = "F", _("zagraniczne")
        DOMESTIC = "D", _("krajowe")

    name = models.CharField(_("nazwa"), max_length=255)
    abbr = models.CharField(_("skrót"), max_length=255)
    kind = models.CharField(
        _("rodzaj"),
        max_length=1,
        choices=KindChoices.choices,
    )

    class Meta:
        verbose_name = _("wydawnictwo")
        verbose_name_plural = _("wydawnictwa")

    def __str__(self):
        return f"{self.name} ({self.abbr})"


class Journal(models.Model):
    """A class to represent Journal objects."""

    publisher = models.ForeignKey(
        to=Publisher,
        on_delete=models.SET_NULL,
        verbose_name=Publisher.opts.verbose_name,
        related_name="journals",
        blank=True,
        null=True,
    )
    title = models.CharField(_("tytuł"), max_length=255)
    abbr = models.CharField(_("skrót"), max_length=255)
    impact_factor = models.DecimalField(
        _("IF"),
        max_digits=6,
        decimal_places=3,
        default=0.0,
        help_text=_("Impact Factor, czynnik wpływu/oddziaływania."),
    )
    rating = models.PositiveSmallIntegerField(
        _("punkty"),
        choices=[(points, points) for points in constants.JOURNAL_RATING_POINTS],
        default=min(constants.JOURNAL_RATING_POINTS),
        help_text=format_lazy(
            '{title} <a href="{url}" target="_blank">{content}</a>',
            title=_("Punkty Ministerstwa Edukacji i Nauki."),
            url=constants.JOURNAL_RATING_URL,
            content=_("Wykaz czasopism"),
        ),
    )
    ancestor = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        verbose_name=_("poprzednik"),
        related_name="successors",
        blank=True,
        null=True,
        help_text=_(
            "Czasopismo, z którego powstało obecnie edytowane/tworzone czasopismo."
        ),
    )

    class Meta:
        verbose_name = _("czasopismo")
        verbose_name_plural = _("czasopisma")

    def __str__(self):
        return "{} {}".format(
            self.title,
            f"({self.abbr})"
            if not self.abbr.casefold() == self.title.casefold()
            else "",
        ).strip()


class Article(Element):
    """A class to represent Article objects."""

    journal = models.ForeignKey(
        to=Journal,
        on_delete=models.CASCADE,
        verbose_name=Journal.opts.verbose_name,
        related_name="articles",
    )
    year = models.PositiveSmallIntegerField(
        _("rok"),
        default=base_utils.get_current_year,
        validators=[
            MinValueValidator(
                limit_value=constants.MIN_ARTICLE_YEAR,
                message=_(
                    "Nie można dodawać artykułów opublikowanych "
                    "przed rokiem %(limit_value)s."
                ),
            ),
        ],
    )
    volume = models.CharField(_("wolumin"), max_length=255, blank=True)
    pages = models.CharField(_("strony"), max_length=255, blank=True)
    doi = models.CharField(
        _("DOI"),
        max_length=255,
        blank=True,
        validators=[
            RegexValidator(
                regex=constants.DOI_REGEX,
                message=_("Niepoprawny format DOI."),
            )
        ],
        help_text=_("Tylko DOI, nie URL z domeną „doi.org”."),
    )
    open_access = models.BooleanField(
        _("OA"),
        default=False,
        choices=models.YesNoQuestionChoices.choices,
        help_text=_("Open Access, artykuł z otwartym dostępem."),
    )

    # Uneditable fields, auto-updated:
    # - by using `clean` method or
    # - `post_save` signal sent by the Journal model (see .signals module)

    _impact_factor = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=0.0,
        editable=False,
    )
    _rating = models.PositiveSmallIntegerField(default=0, editable=False)

    class Meta:
        verbose_name = _("artykuł")
        verbose_name_plural = _("artykuły")

    def clean(self):
        super().clean()

        # Check if the year is not far in the future
        if self.year > (
            limit_value := base_utils.get_current_year()
            + constants.MAX_ARTICLE_YEAR_OFFSET
        ):
            raise ValidationError(
                {
                    "year": _(
                        "Nie można dodawać artykułów opublikowanych "
                        "po roku %(limit_value)s."
                    )
                    % {"limit_value": limit_value}
                }
            )

        # Update the article's `_impact_factor` and `_rating` according to those
        # for the journal
        if hasattr(self, "journal"):
            self._impact_factor, self._rating = (
                self.journal.impact_factor,
                self.journal.rating,
            )

    def get_doi_url(self):
        """Return URL to the article based on its DOI."""
        if self.doi:
            return "{}/{}".format(
                prefix[:-1]
                if (prefix := constants.DOI_URL_PREFIX).endswith("/")
                else prefix,
                self.doi,
            )
