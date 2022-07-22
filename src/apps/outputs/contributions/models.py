from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.employees.models import Employee
from base import models

from .constants import AUTHORS_EMPLOYEES, AUTHORS_NOT_EMPLOYEES, ELEMENT_MODELS


class AuthorGroupChoices(models.TextChoices):
    """Choices enumeration for the `group` field of AuthorStatus Model."""

    EMPLOYEES = AUTHORS_EMPLOYEES, _("autorzy-pracownicy")
    AUTHORS = AUTHORS_NOT_EMPLOYEES, _("autorzy niebędący pracownikami")


class Author(models.Model):
    """A class to represent Author objects."""

    employee = models.ForeignKey(
        to=Employee,
        on_delete=models.SET_NULL,
        verbose_name=Employee.opts.verbose_name,
        blank=True,
        null=True,
    )
    alias = models.CharField(
        _("alias"),
        max_length=255,
        blank=True,
        help_text="%s<br>%s"
        % (
            _(
                "Format: „nazwisko, inicjały”, na przykład: "
                "„Jan Krzysztof Kowalski” → „Kowalski J. K.”"
            ),
            _(
                "W przypadku pracowników, alias może zostać utworzony "
                "automatycznie na podstawie imienia i nazwiska."
            ),
        ),
    )

    class Meta:
        verbose_name = _("autor")
        verbose_name_plural = _("autorzy")
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "alias"],
                name="unique_employee_alias",  # employees must have unique aliases
            )
        ]

    def __str__(self):
        if self.is_employee():
            return "%(alias)s (pracownik: %(employee)s)" % {
                "alias": self.alias,
                "employee": self.employee,
            }
        return self.alias

    def clean(self):
        super().clean()

        # Both `employee` and `alias` fields have `blank` set to True.
        # However, both fields must not be actually empty.
        if not (self.employee_id or self.alias):
            raise ValidationError(
                _(
                    "Utworzenie/zmiana autora wymaga podania aliasu "
                    "lub wskazania pracownika. Oba pola nie mogą zostać puste."
                )
            )

        # Automatically assign the alias based on the employee's data ONLY if the
        # employee is specified whereas the alias is not. Aliases given manually have
        # precedence over the auto-created ones.
        if self.is_employee() and not self.alias:
            self.alias = self.employee.short_name

    def is_employee(self):
        """Check if the author is also an employee."""
        return self.employee is not None

    @property
    def group(self):
        """Return the code of the group the author belongs to."""
        return AUTHORS_EMPLOYEES if self.is_employee() else AUTHORS_NOT_EMPLOYEES

    def get_group_display(self):
        """Return the display version of the group."""
        return AuthorGroupChoices(self.group).label


class AuthorStatus(models.Model):
    """A class to represent AuthorStatus objects."""

    name = models.CharField(_("nazwa"), max_length=255)
    abbr = models.CharField(
        _("skrót"),
        max_length=2,
        help_text=_("Kod jedno- lub dwuliterowy (wielkie litery)."),
    )
    group = models.CharField(
        _("grupa autorów"),
        max_length=max([len(value) for value in AuthorGroupChoices.values]),
        choices=AuthorGroupChoices.choices,
    )
    default = models.YesNoAnswerField(_("domyślny dla grupy"), default=models.NO)

    class Meta:
        verbose_name = _("status autora")
        verbose_name_plural = _("statusy autorów")

    def __str__(self):
        return _(
            "%(name)s (%(abbr)s) dla grupy „%(group)s” %(default_info)s"
        ).rstrip() % {
            "name": self.name,
            "abbr": self.abbr,
            "group": self.get_group_display(),
            "default_info": _("(%s)") % _("domyślny") if self.default else "",
        }

    def clean(self):
        super().clean()

        # Ensure that the `abbr` field value is in uppercase
        if not self.abbr == self.abbr.upper():
            raise ValidationError({"abbr": _("Wymagane tylko wielkie litery.")})

        # Ensure that there is only one default status per group of authors

        # TODO Find a way to implement this a database constraint

        if self.default:
            default_group_statuses = self.opts.model.objects.filter(
                group=self.group,
                default=True,
            ).exclude(pk=self.pk)

            if default_group_statuses.exists():
                default_status = default_group_statuses[0]
                raise ValidationError(
                    {
                        "default": _(
                            "Istnieje już domyślny status dla grupy „%(group)s”; "
                            "statusem tym jest „%(default_status)s”."
                        )
                        % {
                            "group": self.get_group_display(),
                            "default_status": "{name} ({abbr})".format(
                                name=default_status.name,
                                abbr=default_status.abbr,
                            ),
                        }
                    }
                )


class Contribution(models.Model):
    """A class to represent Contribution objects."""

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("rodzaj elementu"),
        related_name="contributions",
        limit_choices_to={
            "app_label__exact": "outputs",
            "model__in": ELEMENT_MODELS,
        },
    )
    object_id = models.PositiveIntegerField(
        _("ID elementu"),
        default=1,
        help_text="%s<br>%s"
        % (
            _("Liczba całkowita większa od 0."),
            _("UWAGA! Proszę nie modyfikować tego pola ręcznie."),
        ),
    )
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_id")
    author = models.ForeignKey(
        to=Author,
        on_delete=models.CASCADE,
        verbose_name=Author.opts.verbose_name,
        related_name="contributions",
    )
    percentage = models.SmallIntegerField(
        verbose_name=_("wkład (%)"),
        validators=[
            MinValueValidator(
                limit_value=0,
                message=_(
                    "Wkład autora musi być liczbą większą/równą %(limit_value)s."
                ),
            ),
            MaxValueValidator(
                limit_value=100,
                message=_(
                    "Wkład autora nie może przekraczać wartości %(limit_value)s%%."
                ),
            ),
        ],
        default=0,
        help_text=_("Liczba całkowita między 0 a 100."),
    )
    author_status = models.ForeignKey(
        AuthorStatus,
        on_delete=models.SET_NULL,
        verbose_name=AuthorStatus.opts.verbose_name,
        related_name="contributions",
        blank=True,
        null=True,
        help_text="%s<br>%s"
        % (
            _(
                "Jeśli status nie zostanie wybrany, "
                "zostanie on ustawiony na status domyślny."
            ),
            _(
                "Upewnij się, że dla wybranej grupy autorów "
                "określony został status domyślny."
            ),
        ),
    )

    class Meta:
        verbose_name = _("udział")
        verbose_name_plural = _("udziały")

    def __str__(self):
        return _(
            "%(author)s%(author_status)s w elemencie typu "
            "„%(content_type)s” (ID = %(object_id)d)"
        ) % {
            "author": self.author,
            "author_status": _(" jako %(status)s") % {"status": author_status}
            if (author_status := self.author_status)
            else "",
            "content_type": self.content_type.model_class().opts.verbose_name,
            "object_id": self.object_id,
        }

    def clean(self):
        super().clean()

        # Check if the ID is higher than 0
        if self.object_id == 0:
            raise ValidationError(
                {"object_id": _("ID elementu musi być liczbą większą od 0.")}
            )

        # Check if the content object exists
        if self.content_type_id:
            model = self.content_type.model_class()
            try:
                model.objects.get(pk=self.object_id)
            except model.DoesNotExist:
                raise ValidationError(
                    {
                        "object_id": _(
                            "Element typu „%(element_type)s” o podanym ID nie istnieje."
                        )
                        % {"element_type": model.opts.verbose_name}
                    }
                )

        # Validate the author's status vs the author (note that some statuses are only
        # for the authors which are also employees).
        if self.author_status_id and self.author_id:
            if not self.author_status.group == self.author.group:
                raise ValidationError(
                    {
                        "author_status": _(
                            "Wybrany status nie jest dozwolony dla "
                            "autorów z grupy „%(group)s”."
                        )
                        % {"group": self.author.get_group_display()}
                    }
                )

        # Assign default status value if the status is not specified explicitly
        if not self.author_status_id and self.author_id:
            lookups = {"group__exact": self.author.group, "default": True}
            try:
                self.author_status = AuthorStatus.objects.get(**lookups)
            except AuthorStatus.DoesNotExist:
                raise ValidationError(
                    {
                        "author_status": format_html(
                            "%s<br>%s"
                            % (
                                _(
                                    "Nie istnieje domyślny status dla autorów z grupy "
                                    "„%(group)s”, do której należy wybrany autor."
                                )
                                % {"group": self.author.get_group_display()},
                                _("Wybierz status ręcznie."),
                            )
                        )
                    }
                )
            except AuthorStatus.MultipleObjectsReturned:
                info = AuthorStatus.opts.app_label, AuthorStatus.opts.model_name
                raise ValidationError(
                    {
                        "author_status": format_html(
                            "%s<br>%s"
                            % (
                                _(
                                    "Dla grupy autorów „%(group)s”, do której należy "
                                    "wybrany autor istnieje więcej niż jeden domyślny "
                                    "status."
                                )
                                % {"group": self.author.get_group_display()},
                                '%s <a href="%s">%s</a> %s'
                                % (
                                    _("Zmień dane"),
                                    "{}?{}".format(
                                        reverse(
                                            "admin:%s_%s_changelist" % info
                                        ),  # TODO Refactor using base model method handling admin URLs (as soon as implemented)  # NOQA
                                        "&".join(
                                            [
                                                f"{key}={value}"
                                                for key, value in lookups.items()
                                            ]
                                        ),
                                    ),
                                    _("statusów"),
                                    _("lub wybierz status ręcznie."),
                                ),
                            )
                        )
                    }
                )

    def by_employee(self):
        """Return boolean indicating if the contribution is given by an
        employee."""
        return self.author.is_employee()
