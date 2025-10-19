#!/usr/bin/env python3
"""
Component Generator for OBCMS/BMMS Frontend
Generates HTMX/Tailwind/Alpine.js components with Bangsamoro color scheme
"""

import argparse
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    TemplateRenderer,
    generate_django_template,
    get_accent_classes,
    parse_fields_string,
    parse_columns_string,
    format_html,
)


def load_config():
    """Load configuration from config.yaml."""
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def generate_modal(args, renderer, config):
    """Generate modal component."""
    context = {
        'modal_id': args.name,
        'title': args.title or args.name.replace('_', ' ').title(),
        'size': args.size or config['component_defaults']['modal']['size'],
        'closeable': args.closeable if args.closeable is not None else config['component_defaults']['modal']['closeable'],
        'backdrop_dismiss': args.backdrop_dismiss if args.backdrop_dismiss is not None else config['component_defaults']['modal']['backdrop_dismiss'],
        'show_footer': config['component_defaults']['modal']['show_footer'],
        'content_template': args.content_template or None,
    }
    
    return renderer.render('modal.html.j2', context)


def generate_data_table(args, renderer, config):
    """Generate data table card component."""
    accent = args.accent or config['component_defaults']['data_table']['accent']
    accent_classes = get_accent_classes(accent)
    
    headers = parse_columns_string(args.columns) if args.columns else []
    
    context = {
        'title': args.title or args.name.replace('_', ' ').title(),
        'icon_class': args.icon or 'fas fa-table',
        'accent_class': accent_classes['header_bg'],
        'headers': headers,
        'show_actions': config['component_defaults']['data_table']['show_actions'],
        'actions_width': config['component_defaults']['data_table']['actions_width'],
        'empty_message': config['component_defaults']['data_table']['empty_message'],
    }
    
    return renderer.render('data_table_card.html.j2', context)


def generate_form(args, renderer, config):
    """Generate form component."""
    fields = parse_fields_string(args.fields) if args.fields else []
    submit_color = args.submit_color or config['component_defaults']['form']['submit_color']
    
    context = {
        'form_id': args.name,
        'title': args.title or args.name.replace('_', ' ').title(),
        'form_action': args.action or '',
        'form_method': args.method or config['component_defaults']['form']['method'],
        'fields': fields,
        'submit_text': args.submit_text or 'Submit',
        'submit_color': submit_color,
        'show_cancel': config['component_defaults']['form']['show_cancel'],
        'cancel_url': args.cancel_url or '#',
    }
    
    return renderer.render('form.html.j2', context)


def generate_stat_card(args, renderer, config):
    """Generate stat card component."""
    accent = args.accent or config['component_defaults']['stat_card']['accent']
    accent_classes = get_accent_classes(accent)
    
    context = {
        'title': args.title or args.name.replace('_', ' ').title(),
        'icon_class': args.icon or 'fas fa-chart-line',
        'accent_classes': accent_classes,
        'value': args.value or '0',
        'change': args.change or None,
        'trend': args.trend or 'neutral',
        'subtitle': args.subtitle or None,
        'link_url': args.link_url or None,
        'link_text': args.link_text or 'View details',
    }
    
    return renderer.render('stat_card.html.j2', context)


def generate_htmx_partial(args, renderer, config):
    """Generate HTMX partial component."""
    fields = parse_columns_string(args.fields) if args.fields else []
    
    context = {
        'partial_id': args.name,
        'entity': args.entity or 'item',
        'fields': fields,
        'actions': args.actions.split(',') if args.actions else ['view', 'edit'],
        'swap': config['component_defaults']['htmx_partial']['swap'],
        'trigger': config['component_defaults']['htmx_partial']['trigger'],
    }
    
    return renderer.render('htmx_partial.html.j2', context)


COMPONENT_GENERATORS = {
    'modal': generate_modal,
    'data_table': generate_data_table,
    'form': generate_form,
    'stat_card': generate_stat_card,
    'htmx_partial': generate_htmx_partial,
}


def main():
    parser = argparse.ArgumentParser(
        description='Generate OBCMS/BMMS frontend components with Bangsamoro color scheme'
    )
    
    parser.add_argument('--type', required=True,
                       choices=['modal', 'data_table', 'form', 'stat_card', 'htmx_partial'],
                       help='Component type to generate')
    parser.add_argument('--name', required=True,
                       help='Component name (e.g., user_profile_modal)')
    parser.add_argument('--output', required=True,
                       help='Output directory path')
    
    parser.add_argument('--title', help='Component title')
    parser.add_argument('--icon', help='FontAwesome icon class')
    parser.add_argument('--accent', help='Accent color (ocean, teal, emerald, gold)')
    
    parser.add_argument('--size', help='Modal size (sm, md, lg, xl, full)')
    parser.add_argument('--closeable', type=bool, help='Modal is closeable')
    parser.add_argument('--backdrop_dismiss', type=bool, help='Dismiss modal on backdrop click')
    parser.add_argument('--content_template', help='Path to modal content template')
    
    parser.add_argument('--columns', help='Comma-separated column names for data tables')
    parser.add_argument('--fields', help='Comma-separated field definitions (name:type)')
    parser.add_argument('--actions', help='Comma-separated action names')
    parser.add_argument('--entity', help='Entity name for HTMX partials')
    
    parser.add_argument('--action', help='Form action URL')
    parser.add_argument('--method', help='Form HTTP method')
    parser.add_argument('--submit_text', help='Submit button text')
    parser.add_argument('--submit_color', help='Submit button color')
    parser.add_argument('--cancel_url', help='Cancel button URL')
    
    parser.add_argument('--value', help='Stat card value')
    parser.add_argument('--change', help='Stat card change percentage')
    parser.add_argument('--trend', choices=['up', 'down', 'neutral'], help='Stat card trend')
    parser.add_argument('--subtitle', help='Stat card subtitle')
    parser.add_argument('--link_url', help='Stat card link URL')
    parser.add_argument('--link_text', help='Stat card link text')
    
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--dry-run', action='store_true', help='Show output without writing file')
    
    args = parser.parse_args()
    
    config = load_config()
    templates_dir = Path(__file__).parent.parent / 'templates'
    renderer = TemplateRenderer(templates_dir)
    
    generator = COMPONENT_GENERATORS.get(args.type)
    if not generator:
        print(f"Error: Unknown component type: {args.type}")
        sys.exit(1)
    
    try:
        content = generator(args, renderer, config)
        
        django_content = generate_django_template(content, args.type, args.name)
        
        output_path = Path(args.output) / f"{args.name}.html"
        
        if args.dry_run:
            print(f"Would write to: {output_path}")
            print("\n" + "="*80)
            print(django_content)
            print("="*80)
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(django_content)
            
            print(f"✅ Generated {args.type} component: {output_path}")
            
            if args.verbose:
                print(f"\nComponent details:")
                print(f"  Type: {args.type}")
                print(f"  Name: {args.name}")
                print(f"  Output: {output_path}")
                if args.accent:
                    print(f"  Accent: {args.accent}")
    
    except Exception as e:
        print(f"❌ Error generating component: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
