from django.contrib import admin
from django.contrib.admin import *  # NOQA


class ModelAdmin(admin.ModelAdmin):
    """Project-wide template to replace the built-in Django's base ModelAdmin."""
