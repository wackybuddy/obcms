"""
Template Utilities for Frontend Component Scaffolder
Handles Jinja2 template rendering and component generation
"""

import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path


class TemplateRenderer:
    """Renders Jinja2 templates for component generation."""
    
    def __init__(self, templates_dir):
        self.templates_dir = Path(templates_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._register_filters()
    
    def _register_filters(self):
        """Register custom Jinja2 filters."""
        self.env.filters['safe_id'] = self._safe_id_filter
        self.env.filters['title_case'] = self._title_case_filter
        self.env.filters['snake_case'] = self._snake_case_filter
    
    @staticmethod
    def _safe_id_filter(value):
        """Convert string to safe HTML ID."""
        return value.lower().replace(' ', '-').replace('_', '-')
    
    @staticmethod
    def _title_case_filter(value):
        """Convert string to title case."""
        return ' '.join(word.capitalize() for word in value.replace('_', ' ').replace('-', ' ').split())
    
    @staticmethod
    def _snake_case_filter(value):
        """Convert string to snake_case."""
        return value.lower().replace(' ', '_').replace('-', '_')
    
    def render(self, template_name, context):
        """
        Render a template with given context.
        
        Args:
            template_name: Name of template file (e.g., 'modal.html.j2')
            context: Dictionary of template variables
        
        Returns:
            Rendered HTML string
        """
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def get_template_path(self, template_name):
        """Get full path to a template file."""
        return self.templates_dir / template_name


def generate_django_template(content, component_type, component_name):
    """
    Wrap rendered content in Django template structure.
    
    Args:
        content: Rendered HTML content
        component_type: Type of component
        component_name: Name of component
    
    Returns:
        Complete Django template string
    """
    header = f"""{{%% load static %%}}
{{# {component_type.replace('_', ' ').title()}: {component_name} #}}

"""
    return header + content


def parse_fields_string(fields_str):
    """
    Parse field definition string into structured format.
    
    Args:
        fields_str: Comma-separated fields like "name:text,email:email,active:checkbox"
    
    Returns:
        List of field dictionaries
    """
    if not fields_str:
        return []
    
    fields = []
    for field_def in fields_str.split(','):
        parts = field_def.strip().split(':')
        if len(parts) != 2:
            continue
        
        field_name, field_type = parts
        fields.append({
            'name': field_name.strip(),
            'type': field_type.strip(),
            'label': field_name.strip().replace('_', ' ').title(),
            'required': True,
        })
    
    return fields


def parse_columns_string(columns_str):
    """
    Parse column definition string into structured format.
    
    Args:
        columns_str: Comma-separated columns like "Name,Email,Status,Actions"
    
    Returns:
        List of column dictionaries
    """
    if not columns_str:
        return []
    
    columns = []
    for col in columns_str.split(','):
        col_name = col.strip()
        columns.append({
            'label': col_name,
            'field': col_name.lower().replace(' ', '_'),
            'width': '',
            'class': 'flex items-center',
        })
    
    return columns


def format_html(html_content, indent_size=2):
    """
    Basic HTML formatting for readability.
    
    Args:
        html_content: HTML string to format
        indent_size: Number of spaces per indent level
    
    Returns:
        Formatted HTML string
    """
    lines = []
    indent_level = 0
    
    for line in html_content.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        
        if stripped.startswith('</') or stripped.startswith('{%'):
            indent_level = max(0, indent_level - 1)
        
        lines.append(' ' * (indent_level * indent_size) + stripped)
        
        if stripped.startswith('<') and not stripped.startswith('</') and not stripped.endswith('/>'):
            if not any(stripped.startswith(tag) for tag in ['<br', '<hr', '<img', '<input']):
                indent_level += 1
    
    return '\n'.join(lines)
