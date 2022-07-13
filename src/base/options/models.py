import os

from django.db import models
from django.db.models import *  # NOQA
from django.urls import reverse


class Model(models.Model):
    """Project-wide template to replace the built-in Django's base Model."""

    class Meta:
        abstract = True

    @classmethod
    @property
    def pk_name(cls):
        """Return the model's PK field name."""
        return cls._meta.pk.name

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

    @classmethod
    def get_static_path(
        cls,
        file_name,
        type_dir=None,
        app=True,
        model=False,
        admin=False,
    ):
        """Return path of a static file.

        The path is constructed on the basis of the model data (app
        label, model name), the file type and the relationship of the
        file with the admin.
        """
        if type_dir is None:
            # Get the name of the type_dir based on the provided file_name extension
            _, file_ext = os.path.splitext(file_name)
            file_ext = file_ext[1:].lower()
            if not file_ext or file_ext in ["css", "js"]:
                type_dir = file_ext
            elif file_ext.lower() in ["jpg", "jpeg", "png", "bmp", "svg"]:
                type_dir = "img"

        # App dir - note that if the the file is associated with the model (`model` is
        # True), app dir must be included regard less of the value of `app` parameter.
        app_dir = cls._meta.app_label if app or model else ""

        return os.path.join(
            "admin" if admin else "",  # file associated with the admin site
            type_dir if admin else app_dir,
            app_dir if admin else type_dir or "",
            cls._meta.model_name if model else "",
            file_name,
        )
