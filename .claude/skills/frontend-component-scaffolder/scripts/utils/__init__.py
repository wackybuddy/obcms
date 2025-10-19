"""
Utility functions for Frontend Component Scaffolder
"""

from .color_utils import (
    get_color_class,
    get_gradient_class,
    get_color_hex,
    get_accent_classes,
    validate_color_usage,
    BANGSAMORO_COLORS,
    GRADIENT_CLASSES,
)

from .template_utils import (
    TemplateRenderer,
    generate_django_template,
    parse_fields_string,
    parse_columns_string,
    format_html,
)

from .validation_utils import (
    ComponentValidator,
    validate_accessibility,
    validate_htmx,
    get_validation_report,
)

__all__ = [
    'get_color_class',
    'get_gradient_class',
    'get_color_hex',
    'get_accent_classes',
    'validate_color_usage',
    'BANGSAMORO_COLORS',
    'GRADIENT_CLASSES',
    'TemplateRenderer',
    'generate_django_template',
    'parse_fields_string',
    'parse_columns_string',
    'format_html',
    'ComponentValidator',
    'validate_accessibility',
    'validate_htmx',
    'get_validation_report',
]
