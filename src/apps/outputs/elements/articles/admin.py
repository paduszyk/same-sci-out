from base import admin

from .forms import ArticleAdminChangeForm
from .models import Article, Journal, Publisher


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """A class to specify admin options for the Publisher model."""


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    """A class to specify admin options for the Journal model."""


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """A class to specify admin options for the Article model."""

    form = ArticleAdminChangeForm
