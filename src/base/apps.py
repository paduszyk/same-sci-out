from django.contrib.admin.apps import AdminConfig


class AdminConfig(AdminConfig):
    """A class to override default `django.contrib.admin` app configuration."""

    # Update the default AdminSite object
    default_site = "base.sites.AdminSite"
