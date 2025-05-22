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
│   ├── obc_management/     # Main Django project
│   ├── common/             # Common utilities and base models
│   ├── communities/        # OBC community management
│   ├── mana/              # Mapping and Needs Assessment
│   ├── coordination/      # Stakeholder coordination
│   ├── policies/          # Policy recommendations
│   ├── templates/         # HTML templates
│   └── static/           # Static files (CSS, JS, images)
├── requirements/          # Python dependencies
├── scripts/              # Project scripts and documentation
├── docs/                 # Project documentation
└── venv/                # Python virtual environment
```

## Quick Start

### Prerequisites

- Python 3.9+
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
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

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
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000`

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

### 4. Policies Module
- **Purpose**: Evidence-based policy recommendations
- **Features**: Recommendation tracking, approval workflows, impact assessment

## Development

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