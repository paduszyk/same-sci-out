from django.contrib.admin.apps import AdminConfig


class AdminConfig(AdminConfig):
    """Class representing the default admin app and its configuration."""

    default_site = "base.admin.AdminSite"
