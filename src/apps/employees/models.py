from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.units.models import Department
from base import models

from . import constants, utils


class EmployeeStatus(models.Model):
    """A class to represent EmployeeStatus objects."""

    name = models.CharField(_("nazwa"), max_length=255)
    abbr = models.CharField(
        _("skrót"),
        max_length=2,
        help_text=_("Kod jedno- lub dwuliterowy (wielkie litery)."),
    )

    class Meta:
        verbose_name = _("status pracownika")
        verbose_name_plural = _("statusy pracowników")

    def __str__(self):
        return f"{self.name} ({self.abbr})"

    def clean(self):
        super().clean()

        # Ensure that the `abbr` field value is in uppercase
        if not self.abbr == self.abbr.upper():
            raise ValidationError({"abbr": _("Wymagane tylko wielkie litery.")})


class EmployeeGroup(models.Model):
    """A class to represent EmployeeGroup objects."""

    name = models.CharField(
        _("nazwa"),
        max_length=255,
        help_text=_("Przymiotnik, liczba mnoga, w mianowniku."),
    )
    abbr = models.CharField(_("skrót"), max_length=20)
    teachers = models.YesNoAnswerField(_("nauczyciele"), default=models.YES)

    @property
    def _name_prefix(self):
        """Return a prefix for the employee group's name."""
        return (
            self.opts.get_field("teachers").verbose_name
            if self.teachers
            else _("pracownicy")
        )

    class Meta:
        verbose_name = _("grupa pracowników")
        verbose_name_plural = _("grupy pracowników")

    def __str__(self):
        return f"{self._name_prefix} {self.name} ({self.abbr})"


class Position(models.Model):
    """A class to represent Position objects."""

    name = models.CharField(_("nazwa"), max_length=255)
    groups = models.ManyToManyField(
        to=EmployeeGroup,
        verbose_name=EmployeeGroup.opts.verbose_name_plural,
    )

    class Meta:
        verbose_name = _("stanowisko")
        verbose_name_plural = _("stanowiska")

    def __str__(self):
        return self.name

    def is_teacher(self):
        """Return bool indicating whether for all the Group objects related the
        value of their `teachers` field is True."""
        return all(self.groups.values_list("teachers", flat=True))


class AcademicDegree(models.Model):
    """A class to represent AcademicDegree objects."""

    name = models.CharField(_("nazwa"), max_length=255)

    class Meta:
        verbose_name = _("tytuł/stopień naukowy")
        verbose_name_plural = _("tytuły i stopnie naukowe")

    def __str__(self):
        return self.name


class Discipline(models.Model):
    """A class to represent Discipline objects."""

    class DomainChoices(models.TextChoices):
        """Choices enumeration for the `domain` field."""

        SCI = "SCI", _("nauki ścisłe i przyrodnicze")
        ENG = "ENG", _("nauki inżynieryjno-techniczne")

    name = models.CharField(_("nazwa"), max_length=255)
    abbr = models.CharField(
        _("skrót"),
        max_length=2,
        help_text=_("Kod jedno- lub dwuliterowy (wielkie litery)."),
    )
    domain = models.CharField(
        _("dziedzina naukowa"),
        max_length=max([len(value) for value in DomainChoices.values]),
        choices=DomainChoices.choices,
        default=DomainChoices.SCI,
    )

    class Meta:
        verbose_name = _("dyscyplina naukowa")
        verbose_name_plural = _("dyscypliny naukowe")

    def __str__(self):
        return f"{self.name} ({self.abbr}); {self.get_domain_display()}"

    def clean(self):
        super().clean()

        # Ensure that the `abbr` field value is in uppercase
        if not self.abbr == self.abbr.upper():
            raise ValidationError({"abbr": _("Wymagane tylko wielkie litery.")})


User = get_user_model()


class Employee(models.Model):
    """A class to represent Employee objects."""

    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        verbose_name=User.opts.verbose_name,
        help_text=_("Dane osobowe pracownika zostaną pobrane z profilu użytkownika."),
    )
    status = models.ForeignKey(
        to=EmployeeStatus,
        on_delete=models.CASCADE,
        verbose_name=EmployeeStatus.opts.verbose_name,
        related_name="employees",
    )
    academic_degree = models.ForeignKey(
        to=AcademicDegree,
        on_delete=models.SET_NULL,
        verbose_name=AcademicDegree.opts.verbose_name,
        related_name="employees",
        blank=True,
        null=True,
    )
    in_evaluation = models.YesNoAnswerField(_("w liczbie N"), default=models.YES)
    discipline = models.ForeignKey(
        to=Discipline,
        on_delete=models.SET_NULL,
        verbose_name=Discipline.opts.verbose_name,
        related_name="employees",
        blank=True,
        null=True,
    )
    orcid = models.CharField(
        _("ORCID"),
        max_length=19,
        unique=True,
        blank=True,
        null=True,
        default=None,
        validators=[RegexValidator(constants.ORCID_REGEX)],
        error_messages={"invalid": _("Niepoprawny format numeru ORCID.")},
    )

    class Meta:
        verbose_name = _("pracownik")
        verbose_name_plural = _("pracownicy")

    def __str__(self):
        return (
            "{} {}".format(self.academic_degree or "", self.full_name).strip()
            or self.user.username
        )

    def full_clean(self, *args, **kwargs):
        """Perform a full instance validation."""
        super().full_clean(*args, **kwargs)

        # Perform ORCID checksum validation
        if self.orcid and not utils.check_orcid(self.orcid):
            raise ValidationError(
                {
                    "orcid": _(
                        "Niepoprawny numer ORCID: "
                        "suma kontrolna i ostatnia cyfra nie zgadzają się."
                    )
                }
            )

    @property
    def first_name(self):
        """Return the employee's first name."""
        return self.user.first_name

    @property
    def last_name(self):
        """Return the employee's last name."""
        return self.user.last_name

    @property
    def email(self):
        """Return the employee's first name."""
        return self.user.email

    @property
    def full_name(self):
        """Return the employee's full name."""
        return self.user.get_full_name()

    @property
    def short_name(self):
        """Return the employee's short name."""
        return self.user.get_short_name()

    @property
    def orcid_url(self):
        """Return URL to the employee's ORCID profile."""
        if orcid := self.orcid:
            return utils.get_orcid_url(orcid)

    def is_employed(self):
        """Determine if the employee is employed, i.e. has at least one active
        employment associated."""
        return self.employments.active().exists()

    def get_employment_data(self, active_only=True):
        """Return a list of dicts of the employee's employment data."""
        employments = self.employments
        if active_only:
            employments = employments.active()
        return [
            employment.to_dict(exclude=("id", "employee"))
            for employment in employments.all()
        ]


class Employment(models.Model):
    """A class to represent Employment objects."""

    employee = models.ForeignKey(
        to=Employee,
        on_delete=models.CASCADE,
        verbose_name=Employee.opts.verbose_name,
        related_name="employments",
    )
    position = models.ForeignKey(
        to=Position,
        on_delete=models.CASCADE,
        verbose_name=Position.opts.verbose_name,
        related_name="employments",
    )
    group = models.ForeignKey(
        to=EmployeeGroup,
        on_delete=models.CASCADE,
        verbose_name=EmployeeGroup.opts.verbose_name,
        related_name="employments",
    )
    department = models.ForeignKey(
        to=Department,
        on_delete=models.CASCADE,
        verbose_name=Department.opts.verbose_name,
        related_name="employments",
    )
    since_date = models.DateField(_("od"), blank=True, null=True)
    until_date = models.DateField(_("do"), blank=True, null=True)

    class Meta:
        verbose_name = _("zatrudnienie")
        verbose_name_plural = _("zatrudnienia")

    class Manager(models.Manager):
        def active(self):
            """Get only the active employments.

            This method is a shortcut for applying `is_active` method
            for querysets.
            """
            if (qs := self.get_queryset()).exists():
                return qs.filter(pk__in=[obj.pk for obj in qs if obj.is_active()])

    objects = Manager()

    def __str__(self):
        return _("%(employee)s jako %(position)s w %(department)s") % {
            "employee": self.employee,
            "position": self.full_position_name,
            "department": self.department.get_full_abbr(),
        }

    def clean(self):
        super().clean()

        # First, check if position and group were specified. If not, move on.
        # Note that the checks are based on `_id` attributes. Referring to fields
        # raises RelatedObjectDoesNotExist error.
        if not (self.position_id and self.group_id):
            return None

        # Check if the selected position is within the selected employees groups
        valid_groups = self.position.groups.all()
        if self.group not in valid_groups:
            raise ValidationError(
                {
                    "group": format_html(
                        _(
                            "Wybrane stanowisko (%(position)s) nie należy do tej grupy."
                            "<br>Wybierz jedną z grup: %(groups)s."
                        )
                        % {
                            "position": f"<em>{self.position.name}</em>",
                            "groups": ", ".join(
                                [f"<em>{group.name}</em>" for group in valid_groups]
                            ),
                        }
                    )
                }
            )

        # Check the relationship between since and until dates
        if self.since_date and self.until_date and (self.since_date > self.until_date):
            raise ValidationError(
                {
                    "until_date": _(
                        "Zatrudnienie nie może zakończyć się wcześniej niż się "
                        "rozpoczęło. Ustaw datę %(since_date)s lub późniejszą."
                    )
                    % {"since_date": self.since_date}
                }
            )

    def is_active(self):
        """Check if the employment is active, i.e. whether it has already
        started and is still not expired.

        Missing `since_date` and `until_date` corresponds to started and
        not expired employment by default.
        """
        started, expired = (
            not self.since_date or self.since_date <= timezone.localdate(),
            self.until_date and self.until_date < timezone.localdate(),
        )
        return started and not expired

    @property
    def full_position_name(self):
        """Return the position name along with the position group."""
        return f"{self.position.name} {self.group.abbr}"

    @property
    def faculty(self):
        """Return the employment's faculty."""
        return self.department.faculty

    @property
    def university(self):
        """Return the employment's university."""
        return self.department.university
