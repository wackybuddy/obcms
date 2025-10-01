"""Template tags for task management views."""
from django import template

register = template.Library()


@register.filter
def lookup(dictionary, key):
    """
    Template filter to lookup a dictionary value by key.

    Usage in templates:
        {{ tasks_by_phase|lookup:phase_key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key, [])


@register.filter
def domain_color(domain_code):
    """
    Return Tailwind color class for domain.

    Usage:
        {{ task.domain|domain_color }}
    """
    colors = {
        'mana': 'emerald',
        'coordination': 'blue',
        'policy': 'purple',
        'monitoring': 'amber',
        'services': 'rose',
        'general': 'gray',
    }
    return colors.get(domain_code, 'gray')


@register.filter
def status_color(status_code):
    """
    Return Tailwind color class for task status.

    Usage:
        {{ task.status|status_color }}
    """
    colors = {
        'not_started': 'gray',
        'in_progress': 'blue',
        'on_hold': 'amber',
        'at_risk': 'rose',
        'completed': 'emerald',
        'cancelled': 'gray',
    }
    return colors.get(status_code, 'gray')


@register.filter
def priority_color(priority_code):
    """
    Return Tailwind color class for task priority.

    Usage:
        {{ task.priority|priority_color }}
    """
    colors = {
        'critical': 'rose',
        'high': 'amber',
        'medium': 'blue',
        'low': 'gray',
    }
    return colors.get(priority_code, 'gray')
