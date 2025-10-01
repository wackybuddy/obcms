"""Template helpers for dictionary-style lookups."""

from collections.abc import Mapping, Sequence

from django import template

register = template.Library()


@register.filter(name="get_item")
def get_item(container, key):
    """Safely retrieve ``container[key]`` from mappings or sequences."""

    if container is None:
        return ""

    # Mapping supports .get which already handles missing keys gracefully
    if isinstance(container, Mapping):
        return container.get(key, "")

    try:
        # Sequence lookup covers lists/tuples where ``key`` is an index
        return container[key]  # type: ignore[index]
    except (IndexError, KeyError, TypeError):
        return ""
