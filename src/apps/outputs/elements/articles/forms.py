from django import forms
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from .models import Article


class ArticleAdminChangeForm(forms.ModelForm):
    """A class to represent admin change form of the Article model."""

    class Meta:
        model = Article
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        obj = self.instance

        if obj.pk and obj.doi:
            # Update help text of the `doi` field by adding a link referring to
            # the article via DOI-based URL.
            self.fields["doi"].help_text = (
                self.fields["doi"].help_text
                + "<br>"
                + format_lazy(
                    '<a href="{url}" target="_blank">{content}</a>',
                    url=obj.get_doi_url(),
                    content=_("Zobacz artykuł online"),
                )
            )
