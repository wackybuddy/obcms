"""Template helpers for form rendering."""

from django import template

register = template.Library()


@register.filter
def widget_kind(bound_field):
    """Return the lower-cased widget class name for a bound field."""

    if not hasattr(bound_field, "field"):
        return ""
    widget = getattr(bound_field.field, "widget", None)
    if not widget:
        return ""
    return widget.__class__.__name__.lower()


@register.simple_tag
def resolve_widget(bound_field, override=None):
    """Return the widget type, respecting optional override string."""

    if override:
        return str(override).lower()
    return widget_kind(bound_field)
