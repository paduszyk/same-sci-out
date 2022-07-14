from django import template

from apps.units.apps import UnitsConfig
from apps.units.models import University

register = template.Library()


@register.inclusion_tag("units/snippets/units_tree.html")
def units_tree():
    """Includes ul representing the structure of units saved in the database."""
    return {
        "universities": University.objects.all(),
        "app_verbose_name": UnitsConfig.verbose_name,  # TODO Consider hard-coding this
    }
