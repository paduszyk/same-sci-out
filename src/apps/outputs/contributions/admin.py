from base import admin

from .forms import ContributionAdminChangeForm
from .models import Author, AuthorStatus, Contribution


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """A class to represent admin options for the Author model."""


@admin.register(AuthorStatus)
class AuthorStatusAdmin(admin.ModelAdmin):
    """A class to represent admin options for the AuthorStatus model."""


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    """A class to represent admin options for the Contribution model."""

    form = ContributionAdminChangeForm
