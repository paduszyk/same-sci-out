from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class AdminSite(admin.AdminSite):
    """A class overriding default admin site."""

    name = "admin"

    site_header = _("Baza dorobku pracowników")
    site_title = _("BDP")
    index_title = _("Panel administracyjny")

    def _build_app_dict(self, request, label=None):
        """Update the app data dict used by index and app_index views."""
        app_dict = super()._build_app_dict(request, label)

        # Temporarily convert app_dict to dict to handle context for both
        # `app_index` and `app_list`
        if label:
            app_dict = {label: app_dict}

        # Append extra data on object counts for each model
        for app_label in app_dict:
            for model in app_dict[app_label]["models"]:
                model_admin = self._registry[model["model"]]
                if model_admin.show_objects_count:
                    model.update({"count": model["model"].objects.count()})
                if model["model"].requires_approval():
                    model.update(
                        {
                            "require_approval_count": model["model"]
                            .objects.filter(
                                **{model["model"].APPROVAL_STATUS_FIELD_NAME: False}
                            )
                            .count()
                        }
                    )

        # Return only the data for a specific app is the `label` is not None
        if label:
            app_dict = app_dict.get(app_label)

        return app_dict
