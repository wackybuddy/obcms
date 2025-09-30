"""Additional template filters for text formatting."""

from django import template

register = template.Library()


@register.filter(name="underscore_to_space")
def underscore_to_space(value: str | None) -> str:
    """Convert underscores to spaces for friendlier display labels."""

    if not isinstance(value, str):
        return value
    return value.replace("_", " ")
