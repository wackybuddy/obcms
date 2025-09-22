# OBC Management System

**Other Bangsamoro Communities Management System**

A comprehensive web-based application designed to support the Office for Other Bangsamoro Communities (OOBC) in serving Other Bangsamoro Communities (OBCs) residing outside the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM).

## Project Overview

This system digitalizes the OOBC's core functions including:
- Gathering information and assessing needs of OBCs
- Recommending policies and systematic programs
- Coordinating with stakeholders (BMOAs, LGUs, NGAs)
- Supporting MANA (Mapping and Needs Assessment) activities
- Facilitating evidence-based policy recommendations

## Technology Stack

- **Backend**: Django 4.2+ (Python web framework)
- **Database**: SQLite (upgradeable to PostgreSQL)
- **API**: Django REST Framework
- **Frontend**: Django templates with Tailwind CSS framework
- **Authentication**: Django built-in auth with JWT support
- **File Storage**: Local filesystem with cloud storage capability

## Project Structure

```
OBC-system/
├── src/                    # Django source code
│   ├── obc_management/     # Project settings and URLs
│   ├── common/             # Shared models, forms, and services
│   ├── communities/        # OBC community management
│   ├── coordination/       # Stakeholder coordination
│   ├── mana/               # Mapping and Needs Assessment
│   ├── monitoring/         # Monitoring & evaluation workflows
│   ├── recommendations/    # Recommendations namespace (policies, tracking, docs)
│   ├── templates/          # Project-level templates grouped by app
│   └── static/             # Static assets grouped by app
├── var/                    # Runtime artefacts (SQLite, logs, media)
├── requirements/           # Python dependency locks
├── scripts/                # Project scripts
├── docs/                   # Documentation
└── venv/                   # Local virtual environment
```

## Quick Start

### Prerequisites

- Python 3.12 (see `.python-version`)
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd OBC-system
   ```

2. **Create and activate virtual environment**
   ```bash
   ./scripts/bootstrap_venv.sh       # idempotent helper (macOS/Linux)
   source venv/bin/activate          # On Windows: venv\Scripts\activate
   ```
   > Prefer to do it manually? Use `python3.12 -m venv venv` to ensure the interpreter matches the pinned version.

3. **Install dependencies**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Run database migrations**
   ```bash
   cd src
   ./manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   ./manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   ./manage.py runserver
   ```

The application will be available at `http://localhost:8000`

Runtime data (SQLite database, uploads, and logs) is stored under `var/` so the Django project tree stays focused on code.

## Core Modules

### 1. Communities Module
- **Purpose**: Comprehensive OBC information management
- **Features**: Community profiles, demographic data, stakeholder management, document management

### 2. MANA Module
- **Purpose**: Mapping and Needs Assessment capabilities
- **Features**: Assessment management, needs categorization, priority ranking, baseline studies

### 3. Coordination Module
- **Purpose**: Multi-stakeholder coordination
- **Features**: Stakeholder directory, meeting management, MOA tracking, communication hub

### 4. Recommendations Module
- **Purpose**: Evidence-based policy, program, and service recommendations
- **Features**: Recommendation tracking, approval workflows, knowledge/document repository, impact assessment

### 5. Monitoring & Evaluation Module
- **Purpose**: Track implementation and outcomes of OOBC initiatives
- **Features**: Monitoring entries, update workflows, performance dashboards, evidence attachments

## Development

Templates live in `src/templates/<app>/` and static assets in `src/static/<app>/`, keeping UI files alongside their Django apps.

### Code Style

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting

Run formatting and linting:
```bash
black .
isort .
flake8
```

### Testing

Run tests:
```bash
pytest
```

Run tests with coverage:
```bash
coverage run -m pytest
coverage report
```

Each Django app stores its test suite inside `src/<app>/tests/` to keep scenarios close to the code they cover.

### API Documentation

When the server is running, API documentation is available at:
- Browsable API: `http://localhost:8000/api/`
- Admin interface: `http://localhost:8000/admin/`

## Deployment

### Environment Variables

Key environment variables for production:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgres://user:password@host:port/database
REDIS_URL=redis://host:port/0
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up Redis for Celery background tasks
- [ ] Configure email settings
- [ ] Set up static file serving
- [ ] Configure logging
- [ ] Set up SSL/TLS
- [ ] Configure backup strategy

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is developed for the Office for Other Bangsamoro Communities (OOBC) under the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM).

## Support

For support and questions, please contact the OOBC development team.

---

**BANGSAMORO KA, SAAN KA MAN!** 
*(You are Bangsamoro, wherever you are!)*
