import functools

from django.utils.html import format_html


def as_html(func):
    """Apply `format_html` to the output of the wrapped function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        return format_html(value)

    return wrapper
