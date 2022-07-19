from django.contrib import admin


class AdminSite(admin.AdminSite):
    """A class to override `django.contrib.admin.sites.AdminSite` class, hence
    to provide project-wide customizations of the default admin site object."""
