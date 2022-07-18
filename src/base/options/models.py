import os

from django.db import models
from django.db.models import *  # NOQA
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

APPROVED_FIELD_NAME = "_approved"


class Model(models.Model):
    """Project-wide template to replace the built-in Django's base Model."""

    class Meta:
        abstract = True

    @classmethod
    @property
    def pk_name(cls):
        """Return the model's PK field name."""
        return cls._meta.pk.name

    @classmethod
    def admin_changelist_url(cls):
        """Reverse the object's admin changelist page URL."""
        return reverse(
            "admin:{}_{}_changelist".format(
                cls._meta.app_label,
                cls._meta.model_name,
            )
        )

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
            getattr(self, content or "", content) or str(self),
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

    @classmethod
    def requires_approval(cls):
        """Check if the model objects require approval."""
        return hasattr(cls, APPROVED_FIELD_NAME)


def approval_required(cls):
    """Add a boolean field indicating whether the objects need the staff approval."""
    # Define the name for the field accounting for the approval status
    cls.APPROVED_FIELD_NAME = APPROVED_FIELD_NAME

    models.BooleanField(
        _("zatwierdzono"),
        default=False,
        editable=False,
    ).contribute_to_class(cls, cls.APPROVED_FIELD_NAME)

    def is_approved(self):
        """Check if the object is approved."""
        return getattr(self, cls.APPROVED_FIELD_NAME)

    def approve(self, commit=False):
        """Approve the object."""
        if not self.is_approved():
            setattr(self, cls.APPROVED_FIELD_NAME, True)
            if commit:
                self.save()

    def disapprove(self, commit=False):
        """Disapprove the object."""
        if self.is_approved():
            setattr(self, cls.APPROVED_FIELD_NAME, False)
            if commit:
                self.save()

    def approved_objects_url(self):
        """Return URL to approved objects changelist."""
        return f"{self.admin_changelist_url}?{self.APPROVED_FIELD_NAME}__exact=True"

    def disapproved_objects_url(self):
        """Return URL to disapproved objects changelist."""
        return f"{self.admin_changelist_url}?{self.APPROVED_FIELD_NAME}__exact=False"

    cls.is_approved = is_approved
    cls.approve = approve
    cls.disapprove = disapprove
    cls.approved_objects_url = property(approved_objects_url)
    cls.disapproved_objects_url = property(disapproved_objects_url)

    return cls
