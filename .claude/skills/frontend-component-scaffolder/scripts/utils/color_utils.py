"""
Color Utilities for Frontend Component Scaffolder
Handles Bangsamoro color scheme transformations and validations
"""

BANGSAMORO_COLORS = {
    'ocean': {
        '50': '#e0f2fe',
        '100': '#bae6fd',
        '200': '#7dd3fc',
        '300': '#38bdf8',
        '400': '#0ea5e9',
        '500': '#0284c7',
        '600': '#0369a1',
        '700': '#075985',
        '800': '#0c4a6e',
        '900': '#082f49',
    },
    'teal': {
        '50': '#f0fdfa',
        '100': '#ccfbf1',
        '200': '#99f6e4',
        '300': '#5eead4',
        '400': '#2dd4bf',
        '500': '#14b8a6',
        '600': '#0d9488',
        '700': '#0f766e',
        '800': '#115e59',
        '900': '#134e4a',
    },
    'emerald': {
        '50': '#ecfdf5',
        '100': '#d1fae5',
        '200': '#a7f3d0',
        '300': '#6ee7b7',
        '400': '#34d399',
        '500': '#10b981',
        '600': '#059669',
        '700': '#047857',
        '800': '#065f46',
        '900': '#064e3b',
    },
    'gold': {
        '50': '#fffbeb',
        '100': '#fef3c7',
        '200': '#fde68a',
        '300': '#fcd34d',
        '400': '#fbbf24',
        '500': '#f59e0b',
        '600': '#d97706',
        '700': '#b45309',
        '800': '#92400e',
        '900': '#78350f',
    }
}

GRADIENT_CLASSES = {
    'primary': 'bg-gradient-primary',
    'ocean': 'bg-gradient-ocean',
    'ocean_linear': 'bg-gradient-ocean-linear',
    'ocean_radial': 'bg-gradient-ocean',
    'teal': 'bg-gradient-teal',
    'teal_flow': 'bg-gradient-teal-flow',
    'emerald': 'bg-gradient-emerald',
    'emerald_linear': 'bg-gradient-emerald-linear',
    'emerald_radial': 'bg-gradient-emerald',
    'gold': 'bg-gradient-gold',
    'gold_shine': 'bg-gradient-gold-shine',
    'sunrise': 'bg-gradient-sunrise',
    'hero': 'bg-gradient-hero',
}


def get_color_class(color_name, shade='600', prefix='text'):
    """
    Get Tailwind class for a Bangsamoro color.
    
    Args:
        color_name: Color name (ocean, teal, emerald, gold)
        shade: Color shade (50-900)
        prefix: Class prefix (text, bg, border, ring, etc.)
    
    Returns:
        Tailwind CSS class string
    """
    if color_name not in BANGSAMORO_COLORS:
        raise ValueError(f"Invalid color: {color_name}. Must be one of {list(BANGSAMORO_COLORS.keys())}")
    
    if shade not in BANGSAMORO_COLORS[color_name]:
        raise ValueError(f"Invalid shade: {shade}. Must be one of {list(BANGSAMORO_COLORS[color_name].keys())}")
    
    return f"{prefix}-{color_name}-{shade}"


def get_gradient_class(gradient_name):
    """Get gradient background class."""
    if gradient_name not in GRADIENT_CLASSES:
        available = ', '.join(GRADIENT_CLASSES.keys())
        raise ValueError(f"Invalid gradient: {gradient_name}. Available: {available}")
    
    return GRADIENT_CLASSES[gradient_name]


def get_color_hex(color_name, shade='600'):
    """Get hex color value."""
    if color_name not in BANGSAMORO_COLORS:
        raise ValueError(f"Invalid color: {color_name}")
    
    if shade not in BANGSAMORO_COLORS[color_name]:
        raise ValueError(f"Invalid shade: {shade}")
    
    return BANGSAMORO_COLORS[color_name][shade]


def get_accent_classes(accent_color):
    """
    Get complete set of accent classes for a color scheme.
    
    Returns dict with classes for different component parts.
    """
    return {
        'header_bg': get_gradient_class(accent_color) if accent_color in GRADIENT_CLASSES else get_gradient_class('ocean'),
        'text_primary': get_color_class(accent_color, '700', 'text'),
        'text_secondary': get_color_class(accent_color, '600', 'text'),
        'bg_light': get_color_class(accent_color, '50', 'bg'),
        'bg_medium': get_color_class(accent_color, '100', 'bg'),
        'border': get_color_class(accent_color, '600', 'border'),
        'hover_bg': get_color_class(accent_color, '700', 'hover:bg'),
        'focus_ring': get_color_class(accent_color, '500', 'focus:ring'),
    }


def validate_color_usage(html_content):
    """
    Validate that HTML content uses only Bangsamoro color scheme.
    
    Returns tuple (is_valid, errors)
    """
    errors = []
    
    invalid_colors = [
        'red-', 'blue-', 'green-', 'yellow-', 'purple-', 'pink-',
        'indigo-', 'violet-', 'fuchsia-', 'rose-', 'sky-', 'cyan-',
        'lime-', 'orange-'
    ]
    
    for color in invalid_colors:
        if color in html_content and f'{color}bg' not in html_content:
            errors.append(f"Found non-Bangsamoro color: {color}")
    
    valid_colors = ['ocean-', 'teal-', 'emerald-', 'gold-', 'gray-', 'slate-']
    has_bangsamoro_color = any(color in html_content for color in valid_colors)
    
    if not has_bangsamoro_color and 'bg-gradient' not in html_content:
        errors.append("No Bangsamoro colors detected in component")
    
    return (len(errors) == 0, errors)
