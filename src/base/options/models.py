from django.db import models
from django.db.models import *  # NOQA
from django.urls import reverse


class Model(models.Model):
    """Project-wide template to replace the built-in Django's base Model."""

    class Meta:
        abstract = True

    @property
    def admin_change_url(self):
        """Reverse the object's admin change page URL."""
        return reverse(
            "admin:{}_{}_change".format(
                self._meta.app_label,
                self._meta.model_name,
            ),
            args=(self.id,),
        )

    def get_admin_change_link(self, content=None, **attrs):
        """Return HTML code with a link to the object's admin change page."""
        attrs.update({"href": self.admin_change_url})
        return "<a {}>{}</a>".format(
            " ".join(f'{attr}="{value}"' for attr, value in attrs.items()),
            content or str(self),
        )
