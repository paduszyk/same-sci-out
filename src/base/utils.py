from django.utils import timezone


def get_current_year():
    """Return the current year."""
    return timezone.now().year
