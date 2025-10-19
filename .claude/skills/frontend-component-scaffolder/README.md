# Frontend Component Scaffolder - Quick Start

Generate production-ready OBCMS/BMMS components with the Bangsamoro color scheme in seconds.

## Installation

The skill is already installed in your `.claude/skills` directory. No additional setup required.

## Quick Examples

### Generate a Modal
```bash
python .claude/skills/frontend-component-scaffolder/scripts/generate_component.py \
    --type modal \
    --name user_profile_modal \
    --title "User Profile" \
    --size lg \
    --output src/templates/common/partials/
```

### Generate a Data Table
```bash
python .claude/skills/frontend-component-scaffolder/scripts/generate_component.py \
    --type data_table \
    --name organizations_table \
    --title "Organizations" \
    --icon "fas fa-building" \
    --accent ocean \
    --columns "Name,Type,Location,Status" \
    --output src/templates/coordination/partials/
```

### Generate a Form
```bash
python .claude/skills/frontend-component-scaffolder/scripts/generate_component.py \
    --type form \
    --name partnership_form \
    --title "Create Partnership" \
    --fields "organization:select,contact:text,email:email,date:date" \
    --submit_color ocean \
    --output src/templates/coordination/partials/
```

### Generate a Stat Card
```bash
python .claude/skills/frontend-component-scaffolder/scripts/generate_component.py \
    --type stat_card \
    --name active_count \
    --title "Active Partnerships" \
    --icon "fas fa-handshake" \
    --accent emerald \
    --output src/templates/coordination/partials/
```

## Color Scheme Reference

**Ocean Blue** (Primary) - `ocean-600`, `bg-gradient-ocean`
**Teal** (Secondary) - `teal-600`, `bg-gradient-teal`
**Emerald** (Success) - `emerald-600`, `bg-gradient-emerald`
**Gold** (Warning) - `gold-600`, `bg-gradient-gold`

**Primary Gradient**: `bg-gradient-primary` (Ocean → Teal → Emerald)

## Component Types

- `modal` - Overlay dialogs with Alpine.js
- `data_table` - Data tables with actions
- `form` - Forms with validation
- `stat_card` - Statistics display cards
- `htmx_partial` - HTMX-ready partials
- `card` - Generic content cards
- `button` - Styled buttons
- `badge` - Status badges
- `alert` - Alert/notification components

## Full Documentation

See `SKILL.md` for comprehensive documentation, examples, and advanced usage.

## Support

- Documentation: `.claude/skills/frontend-component-scaffolder/SKILL.md`
- Examples: `.claude/skills/frontend-component-scaffolder/examples/`
- Validation: `python scripts/validate_component.py --file <file>`
