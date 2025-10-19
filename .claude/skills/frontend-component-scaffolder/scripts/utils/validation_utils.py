"""
Validation Utilities for Frontend Component Scaffolder
Provides validation logic for generated components
"""

import re
from typing import Dict, List, Tuple
from pathlib import Path


BANGSAMORO_COLORS = ['ocean', 'teal', 'emerald', 'gold']
VALID_GRADIENTS = [
    'bg-gradient-primary', 'bg-gradient-ocean', 'bg-gradient-ocean-linear',
    'bg-gradient-teal', 'bg-gradient-teal-flow', 'bg-gradient-emerald',
    'bg-gradient-emerald-linear', 'bg-gradient-gold', 'bg-gradient-gold-shine',
    'bg-gradient-sunrise', 'bg-gradient-hero'
]

REQUIRED_ARIA_ATTRIBUTES = {
    'modal': ['role="dialog"', 'aria-modal="true"', 'aria-labelledby'],
    'button': ['aria-label'],
    'form': ['aria-label', 'aria-labelledby'],
    'table': ['role', 'aria-label', 'aria-labelledby'],
}

HTMX_ATTRIBUTES = [
    'hx-get', 'hx-post', 'hx-put', 'hx-patch', 'hx-delete',
    'hx-target', 'hx-swap', 'hx-trigger', 'hx-indicator',
    'hx-confirm', 'hx-select', 'hx-swap-oob'
]


class ComponentValidator:
    """Validates generated components against standards."""
    
    def __init__(self, file_path: Path = None, content: str = None):
        if file_path:
            self.file_path = file_path
            with open(file_path, 'r') as f:
                self.content = f.read()
        elif content:
            self.file_path = None
            self.content = content
        else:
            raise ValueError("Either file_path or content must be provided")
        
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate_all(self) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Run all validations and return results.
        
        Returns: (is_valid: bool, results: Dict[str, List[str]])
        """
        self.validate_color_scheme()
        self.validate_accessibility()
        self.validate_htmx_usage()
        self.validate_responsive_classes()
        self.validate_structure()
        
        is_valid = len(self.errors) == 0
        
        return is_valid, {
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info
        }
    
    def validate_color_scheme(self) -> bool:
        """Validate that component uses only Bangsamoro color scheme."""
        invalid_colors = [
            'red-', 'blue-', 'green-', 'yellow-', 'purple-', 'pink-',
            'indigo-', 'violet-', 'fuchsia-', 'rose-', 'sky-', 'cyan-',
            'lime-', 'orange-', 'amber-'
        ]
        
        found_invalid = []
        for color in invalid_colors:
            pattern = rf'\b(text|bg|border|ring|from|to|via)-{color}\d+'
            matches = re.findall(pattern, self.content)
            if matches:
                found_invalid.extend(matches)
        
        if found_invalid:
            self.errors.append(
                f"Non-Bangsamoro colors found: {', '.join(set(found_invalid))}"
            )
        
        has_bangsamoro = any(
            color in self.content 
            for color in BANGSAMORO_COLORS
        )
        
        has_gradient = any(
            gradient in self.content
            for gradient in VALID_GRADIENTS
        )
        
        if not has_bangsamoro and not has_gradient:
            self.warnings.append(
                "No Bangsamoro colors detected. Component may not follow design system."
            )
        
        return len([e for e in self.errors if 'color' in e.lower()]) == 0
    
    def validate_accessibility(self) -> bool:
        """Validate accessibility attributes."""
        component_type = self._detect_component_type()
        
        if component_type == 'modal':
            if 'role="dialog"' not in self.content:
                self.errors.append("Modal missing role=\"dialog\" attribute")
            if 'aria-modal="true"' not in self.content:
                self.errors.append("Modal missing aria-modal=\"true\" attribute")
            if 'aria-labelledby' not in self.content:
                self.warnings.append("Modal should have aria-labelledby attribute")
        
        interactive_elements = re.findall(
            r'<(button|a|input|select|textarea)[^>]*>',
            self.content
        )
        
        for element in interactive_elements:
            if 'aria-label' not in element and 'aria-labelledby' not in element:
                tag = element.split()[0].strip('<')
                self.warnings.append(
                    f"Interactive element <{tag}> may need aria-label or aria-labelledby"
                )
        
        icons = re.findall(r'<i class="[^"]*fa[^"]*"', self.content)
        for icon in icons:
            if 'aria-hidden="true"' not in icon:
                self.warnings.append(
                    "Decorative icons should have aria-hidden=\"true\""
                )
        
        return len([e for e in self.errors if 'aria' in e.lower() or 'accessibility' in e.lower()]) == 0
    
    def validate_htmx_usage(self) -> bool:
        """Validate HTMX attribute usage."""
        htmx_elements = []
        
        for attr in HTMX_ATTRIBUTES:
            pattern = rf'<[^>]*{attr}="[^"]*"[^>]*>'
            matches = re.findall(pattern, self.content)
            htmx_elements.extend(matches)
        
        if not htmx_elements:
            self.info.append("No HTMX attributes detected (may be a static component)")
            return True
        
        for element in htmx_elements:
            if 'hx-get' in element or 'hx-post' in element:
                if 'hx-target' not in element:
                    self.warnings.append(
                        "HTMX request element should specify hx-target"
                    )
            
            if ('hx-get' in element or 'hx-post' in element or 
                'hx-put' in element or 'hx-delete' in element):
                if 'hx-indicator' not in element:
                    self.info.append(
                        "Consider adding hx-indicator for better UX"
                    )
        
        return True
    
    def validate_responsive_classes(self) -> bool:
        """Validate responsive design classes."""
        responsive_prefixes = ['sm:', 'md:', 'lg:', 'xl:', '2xl:']
        
        has_responsive = any(
            prefix in self.content
            for prefix in responsive_prefixes
        )
        
        if not has_responsive:
            self.warnings.append(
                "No responsive classes detected. Component may not be mobile-friendly."
            )
        
        grid_elements = re.findall(r'grid-cols-\d+', self.content)
        if grid_elements:
            mobile_first = any('grid-cols-1' in self.content)
            if not mobile_first:
                self.warnings.append(
                    "Grid layout should use mobile-first approach (grid-cols-1 then md:grid-cols-X)"
                )
        
        return True
    
    def validate_structure(self) -> bool:
        """Validate component structure and best practices."""
        unclosed_tags = self._check_unclosed_tags()
        if unclosed_tags:
            self.errors.append(
                f"Potentially unclosed tags: {', '.join(unclosed_tags)}"
            )
        
        if '{% load static %}' not in self.content:
            self.info.append(
                "Component should include {% load static %} if using static files"
            )
        
        form_elements = re.findall(r'<form[^>]*>', self.content)
        for form in form_elements:
            if '{% csrf_token %}' not in self.content:
                self.errors.append(
                    "Forms must include {% csrf_token %}"
                )
        
        return len([e for e in self.errors if 'structure' in e.lower() or 'tag' in e.lower()]) == 0
    
    def _detect_component_type(self) -> str:
        """Detect component type from content."""
        if 'modal-backdrop' in self.content:
            return 'modal'
        elif 'data-table-card' in self.content:
            return 'data_table'
        elif '<form' in self.content:
            return 'form'
        elif 'stat-card' in self.content:
            return 'stat_card'
        elif 'hx-target' in self.content:
            return 'htmx_partial'
        else:
            return 'unknown'
    
    def _check_unclosed_tags(self) -> List[str]:
        """Check for potentially unclosed HTML tags."""
        tag_stack = []
        unclosed = []
        
        self_closing = ['img', 'input', 'br', 'hr', 'meta', 'link']
        
        tag_pattern = r'<(/?)(\w+)[^>]*>'
        matches = re.findall(tag_pattern, self.content)
        
        for is_closing, tag in matches:
            if tag.lower() in self_closing:
                continue
            
            if tag.startswith('{'):
                continue
            
            if is_closing == '/':
                if tag_stack and tag_stack[-1] == tag:
                    tag_stack.pop()
                else:
                    unclosed.append(tag)
            else:
                tag_stack.append(tag)
        
        if tag_stack:
            unclosed.extend(tag_stack)
        
        return list(set(unclosed))


def validate_color_usage(html_content: str) -> Tuple[bool, List[str]]:
    """
    Quick validation of color usage in HTML content.
    
    Returns: (is_valid, errors)
    """
    validator = ComponentValidator(content=html_content)
    validator.validate_color_scheme()
    return len(validator.errors) == 0, validator.errors


def validate_accessibility(html_content: str) -> Tuple[bool, List[str]]:
    """
    Quick validation of accessibility in HTML content.
    
    Returns: (is_valid, errors)
    """
    validator = ComponentValidator(content=html_content)
    validator.validate_accessibility()
    return len(validator.errors) == 0, validator.errors


def validate_htmx(html_content: str) -> Tuple[bool, List[str]]:
    """
    Quick validation of HTMX usage in HTML content.
    
    Returns: (is_valid, errors)
    """
    validator = ComponentValidator(content=html_content)
    validator.validate_htmx_usage()
    return len(validator.errors) == 0, validator.errors


def get_validation_report(file_path: Path) -> Dict[str, any]:
    """
    Generate a comprehensive validation report for a component file.
    
    Returns: Dictionary with validation results
    """
    validator = ComponentValidator(file_path=file_path)
    is_valid, results = validator.validate_all()
    
    return {
        'file': str(file_path),
        'is_valid': is_valid,
        'component_type': validator._detect_component_type(),
        'errors': results['errors'],
        'warnings': results['warnings'],
        'info': results['info'],
        'error_count': len(results['errors']),
        'warning_count': len(results['warnings']),
    }
