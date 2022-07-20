from django import forms
from django.urls import reverse
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from .models import Contribution


class ContributionAdminChangeForm(forms.ModelForm):
    """A class to represent admin change form of the Contribution model."""

    class Meta:
        model = Contribution
        fields = "__all__"
        error_messages = {
            "percentage": {
                "invalid": _("Wkład autora musi być liczbą całkowitą."),
            },
            "object_id": {
                "invalid": _("ID elementu musi być liczbą całkowitą."),
                "min_value": _("ID elementu musi być liczbą większą od 0."),
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        obj = self.instance

        if obj.pk:
            # For the saved objects include link to the changeform of the related
            # content object in the helptext
            element_class = obj.content_type.model_class()
            info = element_class.opts.app_label, element_class.opts.model_name

            # TODO Refactor using base model method handling admin URLs (as soon as implemented)  # NOQA

            self.fields["object_id"].help_text = (
                self.fields["object_id"].help_text
                + "<br>"
                + format_lazy(
                    '<a href="{url}">{content}</a>',
                    url=reverse(
                        "admin:{}_{}_change".format(*info),
                        args=(obj.object_id,),
                    ),
                    content=_("Przejdź do elementu."),
                )
            )
