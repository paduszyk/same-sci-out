from django.contrib import admin, messages
from django.contrib.admin import *  # NOQA
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.html import format_html
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _


class ModelAdmin(admin.ModelAdmin):
    """Project-wide template to replace the built-in Django's base ModelAdmin."""

    add_object_phrase = _("dodaj")
    change_object_phrase = _("edytuj")
    object_class_prefix = _("obiekt typu")

    show_objects_count = True

    # Overwrite the base ModelAdmin options
    ordering = ()
    list_display = ()

    def __init__(self, *args, **kwargs):
        """Overwrite the base constructor."""
        super().__init__(*args, **kwargs)

        pk = self.model.pk_name

        # By default, the objects are ordered first by PK-field descending.
        # This displays the newest objects at the top of the changelist.
        ordering = self.ordering or (f"-{pk}",)
        if pk not in [o[1:] if o.startswith("-") else o for o in ordering]:
            ordering = (f"-{pk}", *ordering)
        self.ordering = ordering  # TODO Implement this within `get_ordering` method

    def add_approval_info(self):
        """Check if the model admin regards the model requiring approval."""
        return self.model.requires_approval()

    def get_list_display(self, request):
        """Specify the list of fields to be displayed in the changelist."""
        pk = self.model.pk_name

        # By default, always list PK as the very first column of the changelist,
        # unless the PK field is given in `list_display` option.
        list_display = self.list_display or (pk, "__str__")
        if pk not in list_display:
            list_display = (pk, *list_display)
        if self.add_approval_info():
            list_display = (*list_display, self.model.APPROVAL_STATUS_FIELD_NAME)
        return list_display

    def get_actions(self, request):
        """Override the base class method."""
        # Include the actions for the models requiring approval
        if self.add_approval_info():
            if self.actions is not None:
                self.actions = (
                    *self.actions,
                    "approve_selected",
                    "disapprove_selected",
                )

        actions = super().get_actions(request)

        # Update description of the default `delete_selected` action
        actions["delete_selected"] = (
            *actions["delete_selected"][:2],
            _("Usuń wybrane obiekty"),
        )
        return actions

    def get_list_filter(self, request):
        """Override the base class method."""
        list_filter = super().get_list_filter(request)
        # Include approval filter
        if self.add_approval_info():
            list_filter = (*list_filter, self.model.APPROVAL_STATUS_FIELD_NAME)
        return list_filter

    def get_urls(self):
        """Override the base class method."""
        urls = super().get_urls()

        # Include some extra URLs
        if self.add_approval_info():
            info = self.model._meta.app_label, self.model._meta.model_name

            urls = [
                path(
                    "<path:object_id>/approve/",
                    view=self.approval_view(approve=True),
                    name="%s_%s_approve" % info,
                ),
                path(
                    "<path:object_id>/disapprove/",
                    view=self.approval_view(approve=False),
                    name="%s_%s_disapprove" % info,
                ),
            ] + urls

        return urls

    def approval_view(self, approve=True):
        """Return a view to approve/disapprove the object."""

        def view(request, object_id):
            """A view to be returned."""
            obj = self.get_object(request, object_id)

            if approve:
                obj.approve()
            else:
                obj.disapprove()

            self.message_user(
                request,
                message=format_html(
                    _("Obiekt %s został oznaczony jako %s.")
                    % (
                        obj.get_admin_change_link(),
                        _("zatwierdzony") if approve else _("niezatwierdzony"),
                    )
                ),
                level=messages.SUCCESS,
            )
            return HttpResponseRedirect(redirect_to=obj.admin_change_url)

        return view

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

    @admin.action(description=_("Zatwierdź wybrane obiekty"))
    def approve_selected(self, request, queryset):
        """Approve the selected objects."""
        for obj in queryset.filter(**{self.model.APPROVAL_STATUS_FIELD_NAME: False}):
            obj.approve()

    @admin.action(description=_("Oznacz wybrane obiekty jako niezatwierdzone"))
    def disapprove_selected(self, request, queryset):
        """Disapprove the selected objects."""
        for obj in queryset.filter(**{self.model.APPROVAL_STATUS_FIELD_NAME: True}):
            obj.disapprove()
