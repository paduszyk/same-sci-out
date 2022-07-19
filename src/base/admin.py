from django.contrib import admin
from django.contrib.admin import *  # NOQA


class ModelAdmin(admin.ModelAdmin):
    """A class to override `django.contrib.admin.ModelAdmin` class, hence to
    provide project-wide customizations of the default model-admins."""
