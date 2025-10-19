#!/usr/bin/env python3
"""
Component Modifier for OBCMS/BMMS Frontend
Modifies existing components while preserving custom changes
"""

import argparse
import sys
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

sys.path.insert(0, str(Path(__file__).parent))

from utils import get_accent_classes, parse_fields_string, parse_columns_string


class ComponentModifier:
    """Handles modification of existing components."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        if not self.file_path.exists():
            raise FileNotFoundError(f"Component file not found: {file_path}")
        
        with open(self.file_path, 'r') as f:
            self.content = f.read()
        
        self.original_content = self.content
        self.changes = []
    
    def detect_component_type(self) -> str:
        """Detect the type of component from content."""
        if 'modal-backdrop' in self.content or 'x-data="{ show:' in self.content:
            return 'modal'
        elif 'data-table-card' in self.content:
            return 'data_table'
        elif '<form' in self.content and 'form-field' in self.content:
            return 'form'
        elif 'stat-card' in self.content or ('text-3xl' in self.content and 'font-bold' in self.content):
            return 'stat_card'
        elif 'hx-target' in self.content and 'hx-swap' in self.content:
            return 'htmx_partial'
        else:
            return 'unknown'
    
    def change_accent(self, new_accent: str) -> None:
        """Change the accent color of the component."""
        accent_classes = get_accent_classes(new_accent)
        
        old_gradients = [
            'bg-gradient-ocean', 'bg-gradient-teal', 
            'bg-gradient-emerald', 'bg-gradient-gold',
            'bg-gradient-primary'
        ]
        
        for old_gradient in old_gradients:
            if old_gradient in self.content:
                self.content = self.content.replace(
                    old_gradient, 
                    accent_classes['header_bg']
                )
                self.changes.append(f"Changed gradient from {old_gradient} to {accent_classes['header_bg']}")
        
        color_patterns = [
            (r'text-(ocean|teal|emerald|gold)-(\d+)', f'text-{new_accent}-\\2'),
            (r'bg-(ocean|teal|emerald|gold)-(\d+)', f'bg-{new_accent}-\\2'),
            (r'border-(ocean|teal|emerald|gold)-(\d+)', f'border-{new_accent}-\\2'),
            (r'hover:bg-(ocean|teal|emerald|gold)-(\d+)', f'hover:bg-{new_accent}-\\2'),
            (r'focus:ring-(ocean|teal|emerald|gold)-(\d+)', f'focus:ring-{new_accent}-\\2'),
        ]
        
        for pattern, replacement in color_patterns:
            new_content, count = re.subn(pattern, replacement, self.content)
            if count > 0:
                self.content = new_content
                self.changes.append(f"Updated {count} color class(es) to {new_accent}")
    
    def set_backdrop_dismiss(self, enabled: bool) -> None:
        """Enable or disable backdrop dismiss for modals."""
        component_type = self.detect_component_type()
        if component_type != 'modal':
            raise ValueError("Backdrop dismiss is only applicable to modal components")
        
        value = 'true' if enabled else 'false'
        
        self.content = re.sub(
            r'data-backdrop-dismiss="(true|false)"',
            f'data-backdrop-dismiss="{value}"',
            self.content
        )
        
        if enabled:
            if '@click.self' not in self.content:
                self.content = re.sub(
                    r'(<div[^>]*class="modal-backdrop[^>]*)',
                    r'\1 @click.self="show = false; setTimeout(() => { const root = $el.closest(\'.modal-backdrop\'); if (root) { root.remove(); } }, 200)"',
                    self.content
                )
        else:
            self.content = re.sub(
                r'@click\.self="[^"]*"',
                '',
                self.content
            )
        
        self.changes.append(f"Set backdrop dismiss to {value}")
    
    def add_field(self, field_def: str) -> None:
        """Add a new field to a form component."""
        component_type = self.detect_component_type()
        if component_type != 'form':
            raise ValueError("Adding fields is only applicable to form components")
        
        fields = parse_fields_string(field_def)
        if not fields:
            raise ValueError(f"Invalid field definition: {field_def}")
        
        field = fields[0]
        
        field_html = self._generate_field_html(field)
        
        form_actions_pattern = r'(<div[^>]*class="[^"]*flex[^"]*items-center[^"]*justify-end[^"]*gap-3[^"]*pt-4[^"]*border-t[^"]*">)'
        
        self.content = re.sub(
            form_actions_pattern,
            f'{field_html}\n\n    \\1',
            self.content
        )
        
        self.changes.append(f"Added field: {field['name']} ({field['type']})")
    
    def _generate_field_html(self, field: Dict[str, Any]) -> str:
        """Generate HTML for a form field."""
        html_parts = [
            '    <div class="form-field">',
            f'        <label for="form-{field["name"]}" class="block text-sm font-medium text-gray-700 mb-1">',
            f'            {field["label"]}',
        ]
        
        if field.get('required'):
            html_parts.append('            <span class="text-rose-600">*</span>')
        
        html_parts.append('        </label>')
        
        if field['type'] in ['text', 'email', 'tel', 'url']:
            html_parts.extend([
                f'        <input type="{field["type"]}"',
                f'               id="form-{field["name"]}"',
                f'               name="{field["name"]}"',
            ])
            if field.get('required'):
                html_parts.append('               required')
            html_parts.extend([
                '               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-ocean-500 focus:border-ocean-600 transition-colors">',
                '    </div>'
            ])
        
        elif field['type'] == 'textarea':
            html_parts.extend([
                f'        <textarea id="form-{field["name"]}"',
                f'                  name="{field["name"]}"',
                '                  rows="4"',
            ])
            if field.get('required'):
                html_parts.append('                  required')
            html_parts.extend([
                '                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-ocean-500 focus:border-ocean-600 transition-colors"></textarea>',
                '    </div>'
            ])
        
        elif field['type'] == 'select':
            html_parts.extend([
                f'        <select id="form-{field["name"]}"',
                f'                name="{field["name"]}"',
            ])
            if field.get('required'):
                html_parts.append('                required')
            html_parts.extend([
                '                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-ocean-500 focus:border-ocean-600 transition-colors">',
                f'            <option value="">Select {field["label"]}</option>',
                '        </select>',
                '    </div>'
            ])
        
        return '\n'.join(html_parts)
    
    def change_title(self, new_title: str) -> None:
        """Change the title of the component."""
        title_patterns = [
            (r'<h2[^>]*>([^<]+)</h2>', f'<h2\\1>{new_title}</h2>'),
            (r'<h3[^>]*>([^<]+)</h3>', f'<h3\\1>{new_title}</h3>'),
        ]
        
        for pattern, replacement in title_patterns:
            new_content, count = re.subn(pattern, new_title, self.content, count=1)
            if count > 0:
                self.content = new_content
                self.changes.append(f"Changed title to: {new_title}")
                break
    
    def save(self, backup: bool = True) -> None:
        """Save changes to the component file."""
        if backup:
            backup_path = self.file_path.with_suffix('.html.bak')
            with open(backup_path, 'w') as f:
                f.write(self.original_content)
            print(f"💾 Backup saved to: {backup_path}")
        
        with open(self.file_path, 'w') as f:
            f.write(self.content)
    
    def get_diff(self) -> str:
        """Get a diff of the changes."""
        import difflib
        
        diff = difflib.unified_diff(
            self.original_content.splitlines(keepends=True),
            self.content.splitlines(keepends=True),
            fromfile=str(self.file_path),
            tofile=str(self.file_path),
            lineterm=''
        )
        
        return ''.join(diff)


def main():
    parser = argparse.ArgumentParser(
        description='Modify existing OBCMS/BMMS frontend components'
    )
    
    parser.add_argument('--file', required=True,
                       help='Path to component file to modify')
    
    parser.add_argument('--change-accent', metavar='COLOR',
                       help='Change accent color (ocean, teal, emerald, gold)')
    parser.add_argument('--change-title', metavar='TITLE',
                       help='Change component title')
    parser.add_argument('--add-field', metavar='FIELD',
                       help='Add field to form (format: name:type)')
    parser.add_argument('--set-backdrop-dismiss', type=bool, metavar='BOOL',
                       help='Enable/disable backdrop dismiss for modals')
    
    parser.add_argument('--preserve-custom', action='store_true',
                       help='Attempt to preserve custom modifications')
    parser.add_argument('--no-backup', action='store_true',
                       help='Do not create backup file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show changes without saving')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        modifier = ComponentModifier(Path(args.file))
        
        if args.verbose:
            component_type = modifier.detect_component_type()
            print(f"📝 Component type detected: {component_type}")
        
        if args.change_accent:
            modifier.change_accent(args.change_accent)
        
        if args.change_title:
            modifier.change_title(args.change_title)
        
        if args.add_field:
            modifier.add_field(args.add_field)
        
        if args.set_backdrop_dismiss is not None:
            modifier.set_backdrop_dismiss(args.set_backdrop_dismiss)
        
        if not modifier.changes:
            print("⚠️  No changes specified")
            return
        
        print("\n📋 Changes to be applied:")
        for change in modifier.changes:
            print(f"  - {change}")
        
        if args.dry_run or args.verbose:
            print("\n" + "="*80)
            print("DIFF:")
            print("="*80)
            print(modifier.get_diff())
            print("="*80)
        
        if not args.dry_run:
            modifier.save(backup=not args.no_backup)
            print(f"\n✅ Component modified successfully: {args.file}")
        else:
            print("\n🔍 Dry run - no changes saved")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
