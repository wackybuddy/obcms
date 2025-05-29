# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ultrathink

Always use "Ultrathink" whenever you are responding or coding in Claude Code to show your thinking process. No exception.

## Development Environment Setup

**Virtual Environment**: Always work from `venv/` directory
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Working Directory**: All Django commands must be run from the `src/` directory
```bash
cd src
python manage.py [command]
```

## Common Development Commands

### Database Operations
```bash
cd src
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Development Server
```bash
cd src
python manage.py runserver
# Server runs at http://localhost:8000
# Admin interface: http://localhost:8000/admin/
```

### Code Quality and Testing
```bash
# Code formatting and linting
black .
isort .
flake8

# Testing
pytest
coverage run -m pytest
coverage report
```

### Dependencies
```bash
# Install development dependencies
pip install -r requirements/development.txt

# Install production dependencies only
pip install -r requirements/base.txt
```

## Architecture Overview

### Django Project Structure
- **Main Project**: `src/obc_management/` - Django settings and main configuration
- **Applications**: Each module is a separate Django app with models, views, admin, and migrations
- **Environment**: Uses `django-environ` for environment variable management with `.env` file

### Core Applications
1. **common**: Base models, utilities, and shared functionality
2. **communities**: OBC (Other Bangsamoro Communities) profile and demographic management
3. **mana**: Mapping and Needs Assessment functionality 
4. **coordination**: Multi-stakeholder coordination and partnership management
5. **policies**: Policy recommendation tracking and evidence-based proposals

### Key Technical Components
- **Authentication**: Django built-in auth + JWT (SimpleJWT) for API access
- **API**: Django REST Framework with pagination, filtering, and browsable interface
- **Database**: SQLite for development, configurable for PostgreSQL production
- **Background Tasks**: Celery with Redis broker for async operations
- **Logging**: File and console logging configured, logs written to `src/logs/`

## Domain-Specific Context

### OOBC Mission
This system supports the Office for Other Bangsamoro Communities (OOBC) serving Bangsamoro communities outside BARMM (Bangsamoro Autonomous Region in Muslim Mindanao). 

### Geographic Scope
- Primary focus: Regions IX (Zamboanga Peninsula) and XII (SOCCSKSARGEN)
- Administrative hierarchy: Region > Province > Municipality > Barangay
- Timezone: Asia/Manila

### Cultural Considerations
- Islamic education integration (Madaris, Arabic teachers)
- Halal industry and traditional crafts
- Cultural and religious information management
- Respect for Bangsamoro cultural practices in UI/UX

### Assessment Areas (MANA)
- Education (scholarships, Islamic education)
- Economic Development (Halal industry, MSMEs, agriculture/fisheries)
- Social Development (TABANG, AMBag programs)
- Cultural Development (heritage preservation, traditional crafts)
- Infrastructure (healthcare, utilities, roads)

## Environment Configuration

### Required Environment Variables
```env
SECRET_KEY=your-secret-key
DEBUG=True/False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///path/to/db (or postgres://...)
REDIS_URL=redis://localhost:6379/0
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Settings Configuration
- **Debug Toolbar**: Automatically enabled in DEBUG mode
- **CORS**: Configured for localhost development
- **JWT**: 1-hour access tokens, 7-day refresh tokens
- **Pagination**: 20 items per page default

## Development Guidelines

### Model Relationships
- Use timezone-aware datetime fields (`USE_TZ = True`)
- Follow Django naming conventions for models and fields
- Implement proper `__str__` methods for admin interface
- Use foreign keys and many-to-many relationships appropriately for stakeholder connections

### API Development
- All APIs require authentication by default
- Use DRF filtering, searching, and ordering
- Implement proper serializers with validation
- Follow REST principles for URL patterns

### Frontend Integration
- Templates in `src/templates/` with Django template language
- Static files in `src/static/` served during development
- Uses Tailwind CSS for responsive, government-appropriate styling
- Support for dark mode and accessibility (WCAG 2.1 AA)