from django.contrib import admin
from django.contrib.admin import *  # NOQA
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _


class ModelAdmin(admin.ModelAdmin):
    """Project-wide template to replace the built-in Django's base ModelAdmin."""

    add_object_phrase = _("dodaj")
    change_object_phrase = _("edytuj")
    object_class_prefix = _("obiekt typu")

    def changeform_view(self, request, object_id, form_url, extra_context=None):
        """Override the base class method."""
        extra_context = extra_context or {}

        # Overwrite the context variables used in the object's changeform rendering
        extra_context.update(
            {
                "title": " ".join(
                    [
                        str(s)
                        for s in [
                            capfirst(
                                self.change_object_phrase
                                if object_id
                                else self.add_object_phrase
                            ),
                            self.object_class_prefix,
                            capfirst(self.model._meta.verbose_name),
                        ]
                    ]
                ),
                "subtitle": "{} #{}: {}".format(
                    capfirst(self.model._meta.verbose_name),
                    object_id,
                    self.get_object(request, object_id),
                )
                if object_id
                else None,
            }
        )
        return super().changeform_view(request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        """Override the base class method."""
        extra_context = extra_context or {}

        # Overwrite the context variables used in the object's changelist rendering
        extra_context.update(
            {
                "title": _("%s: Wybierz obiekt/obiekty do edycji")
                % capfirst(self.model._meta.verbose_name_plural)
            }
        )
        return super().changelist_view(request, extra_context)
