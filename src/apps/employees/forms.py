from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from .models import Employee, Position


class PositionAdminChangeForm(forms.ModelForm):
    """A class to represent admin change form of the Position model."""

    class Meta:
        model = Position
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Update the help text for the `groups` field
        self.fields["groups"].help_text = (
            "Wybierz tylko grupy należące lub nienależące do grupy nauczycieli."
            + "<br>"
            + self.fields["groups"].help_text
        )

    def clean(self):
        cleaned_data = super().clean()

        if groups := cleaned_data.get("groups", None):
            teachers = groups.values_list("teachers", flat=True)
            if not (all(teachers) or not any(teachers)):
                raise ValidationError(
                    {
                        "groups": _(
                            "Wszystkie wybrane grupy muszą należeć lub "
                            "nie należeć do grupy nauczycieli."
                        )
                    }
                )

        return cleaned_data


class EmployeeAdminChangeForm(forms.ModelForm):
    """A class to represent admin change form of the Employee model."""

    class Meta:
        model = Employee
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        obj = self.instance

        # Include the link to the ORCID profile as a help texts for `orcid` field
        if obj.pk and obj.orcid:
            self.fields["orcid"].help_text = format_lazy(
                '<a href="{url}" target="_blank">{content}</a>',
                url=obj.orcid_url,
                content=_("Przejdź do profilu ORCID pracownika."),
            )
