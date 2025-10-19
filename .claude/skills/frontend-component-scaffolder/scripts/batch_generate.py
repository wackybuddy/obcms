#!/usr/bin/env python3
"""
Batch Component Generator for OBCMS/BMMS Frontend
Generates multiple components from YAML configuration file
"""

import argparse
import sys
from pathlib import Path
import yaml
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from generate_component import COMPONENT_GENERATORS, load_config
from utils import TemplateRenderer


class ComponentConfig:
    """Represents a single component configuration."""
    
    def __init__(self, config_dict: Dict[str, Any]):
        self.type = config_dict.get('type')
        self.name = config_dict.get('name')
        self.output = config_dict.get('output')
        self.title = config_dict.get('title')
        self.icon = config_dict.get('icon')
        self.accent = config_dict.get('accent')
        self.size = config_dict.get('size')
        self.closeable = config_dict.get('closeable')
        self.backdrop_dismiss = config_dict.get('backdrop_dismiss')
        self.content_template = config_dict.get('content_template')
        self.columns = config_dict.get('columns')
        self.fields = config_dict.get('fields')
        self.actions = config_dict.get('actions')
        self.entity = config_dict.get('entity')
        self.action = config_dict.get('action')
        self.method = config_dict.get('method')
        self.submit_text = config_dict.get('submit_text')
        self.submit_color = config_dict.get('submit_color')
        self.cancel_url = config_dict.get('cancel_url')
        self.value = config_dict.get('value')
        self.change = config_dict.get('change')
        self.trend = config_dict.get('trend')
        self.subtitle = config_dict.get('subtitle')
        self.link_url = config_dict.get('link_url')
        self.link_text = config_dict.get('link_text')
    
    def validate(self) -> List[str]:
        """Validate component configuration."""
        errors = []
        
        if not self.type:
            errors.append(f"Component missing 'type' field")
        elif self.type not in COMPONENT_GENERATORS:
            errors.append(f"Invalid component type: {self.type}")
        
        if not self.name:
            errors.append(f"Component missing 'name' field")
        
        if not self.output:
            errors.append(f"Component missing 'output' field")
        
        return errors


def load_batch_config(config_file: Path) -> Dict[str, Any]:
    """Load batch configuration from YAML file."""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration file: {e}")
        sys.exit(1)


def generate_component_from_config(comp_config: ComponentConfig, renderer: TemplateRenderer, 
                                   config: Dict[str, Any], verbose: bool = False) -> tuple:
    """
    Generate a single component from configuration.
    
    Returns: (success: bool, output_path: Path, error_message: str)
    """
    try:
        generator = COMPONENT_GENERATORS.get(comp_config.type)
        if not generator:
            return False, None, f"Unknown component type: {comp_config.type}"
        
        content = generator(comp_config, renderer, config)
        
        from utils import generate_django_template
        django_content = generate_django_template(content, comp_config.type, comp_config.name)
        
        output_path = Path(comp_config.output) / f"{comp_config.name}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(django_content)
        
        return True, output_path, None
        
    except Exception as e:
        return False, None, str(e)


def main():
    parser = argparse.ArgumentParser(
        description='Batch generate OBCMS/BMMS frontend components from YAML configuration'
    )
    
    parser.add_argument('--config', '-c', required=True,
                       help='Path to YAML configuration file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate configuration without generating files')
    parser.add_argument('--continue-on-error', action='store_true',
                       help='Continue generating even if some components fail')
    
    args = parser.parse_args()
    
    config_file = Path(args.config)
    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        sys.exit(1)
    
    print(f"📋 Loading configuration from: {config_file}")
    batch_config = load_batch_config(config_file)
    
    if 'components' not in batch_config:
        print("❌ Configuration file must contain 'components' key")
        sys.exit(1)
    
    components = []
    validation_errors = []
    
    for idx, comp_dict in enumerate(batch_config['components']):
        comp_config = ComponentConfig(comp_dict)
        errors = comp_config.validate()
        
        if errors:
            validation_errors.append(f"Component {idx + 1}: {', '.join(errors)}")
        else:
            components.append(comp_config)
    
    if validation_errors:
        print("\n❌ Configuration validation errors:")
        for error in validation_errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print(f"✅ Configuration valid: {len(components)} component(s) to generate")
    
    if args.dry_run:
        print("\n📝 Dry run - components to be generated:")
        for comp in components:
            print(f"  - {comp.type}: {comp.name} → {comp.output}/{comp.name}.html")
        return
    
    config = load_config()
    templates_dir = Path(__file__).parent.parent / 'templates'
    renderer = TemplateRenderer(templates_dir)
    
    print("\n🚀 Generating components...")
    
    success_count = 0
    failed_count = 0
    results = []
    
    for idx, comp in enumerate(components, 1):
        if args.verbose:
            print(f"\n[{idx}/{len(components)}] Generating {comp.type}: {comp.name}")
        
        success, output_path, error = generate_component_from_config(
            comp, renderer, config, args.verbose
        )
        
        if success:
            success_count += 1
            results.append(('✅', comp.type, comp.name, str(output_path)))
            if not args.verbose:
                print(f"  ✅ {comp.type}: {comp.name}")
        else:
            failed_count += 1
            results.append(('❌', comp.type, comp.name, error))
            print(f"  ❌ {comp.type}: {comp.name} - {error}")
            
            if not args.continue_on_error:
                print("\n❌ Stopping due to error (use --continue-on-error to continue)")
                sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"📊 Generation Summary:")
    print(f"  Total: {len(components)}")
    print(f"  Success: {success_count}")
    print(f"  Failed: {failed_count}")
    
    if args.verbose and results:
        print(f"\n📝 Detailed Results:")
        for status, comp_type, name, detail in results:
            print(f"  {status} {comp_type}: {name}")
            if status == '❌':
                print(f"     Error: {detail}")
            else:
                print(f"     Output: {detail}")
    
    if failed_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
