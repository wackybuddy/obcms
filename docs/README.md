# OBC Management System Documentation

## Overview

The Other Bangsamoro Communities (OBC) Management System is a comprehensive web-based platform designed to support the Office for Other Bangsamoro Communities (OOBC) in managing and coordinating services for Bangsamoro communities outside the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM).

## Documentation Index

### Administrator Operations
- [Installation Guide](admin-guide/installation.md)

### Deployment & Infrastructure
- [Coolify Deployment Plan](deployment/coolify-deployment-plan.md)
- [Coolify Deployment Checklist](deployment/deployment-coolify.md)
- [Docker Guide](deployment/docker-guide.md)
- [PostgreSQL Migration Guide](deployment/postgres-migration-guide.md)
- [Environment Runbooks](env/)

### Program Guidelines
- [Assistance Program Guidelines](guidelines/OBC_guidelines_assistance.md)
- [MANA Implementation Guidelines](guidelines/OBC_guidelines_mana.md)
- [Policy Coordination Guidelines](guidelines/OBC_guidelines_policy.md)

### Product Roadmap & Strategy
- [OBCMS MVP Scope](product/obcMS-MVP.md)
- [OBCMS Summary](product/obcMS-summary.md)
- [Improvement Planning Notes](improvements/)

### Reports & Research
- [OBC Upgrade Proposal](reports/OBC-upgrade.md)
- [OBC Briefing Deck](reports/OBC_briefer.md)
- [OBC Data Overview](reports/OBCdata.md)
- [OOBC Integrative Report](reports/OOBC_integrative_report.md)
- [System Requirements](reports/obc-system-requirements.md)
- [Staff Task Board Research](reports/staff_task_board_research.md)

### UI & Experience
- [Admin Interface Guide](ui/admin-interface-guide.md)
- [Component Library](ui/component-library.md)
- [UI Design System](ui/ui-design-system.md)
- [UI Documentation](ui/ui-documentation.md)

## System Architecture

The OBC Management System is built using modern web technologies:

- **Backend**: Django 4.2+ (Python web framework)
- **Database**: PostgreSQL (with SQLite for development)
- **Frontend**: HTML5, CSS3, JavaScript with Bootstrap
- **API**: Django REST Framework
- **Authentication**: JWT (JSON Web Tokens)
- **Deployment**: Docker, Nginx, Gunicorn

## Core Modules

### 1. Community Management
- OBC community profiles and demographics
- Geographic information and administrative hierarchy
- Community stakeholder management
- Livelihood and infrastructure tracking

### 2. MANA (Mapping and Needs Assessment)
- Comprehensive needs assessment tools
- Community mapping and visualization
- Baseline studies and data collection
- Survey management and analysis

### 3. Coordination and Collaboration
- Multi-stakeholder engagement tracking
- Meeting and event management
- Partnership and MOA/MOU management
- Communication and coordination tools

### 4. Policy Tracking
- Policy recommendation lifecycle management
- Evidence-based policy development
- Impact assessment and monitoring
- Document management and version control

### 5. Data Management
- Data import and export tools
- Field mapping and validation
- Backup and recovery procedures
- Data quality management

## Support

For technical support or questions:

- Email: support@oobc.barmm.gov.ph
- Phone: +63 (64) 421-1977
- Address: OOBC Building, Cotabato City, Maguindanao del Norte

## Version Information

- **Current Version**: 1.0.0
- **Release Date**: 2024
- **License**: Government of the Philippines
- **Maintained by**: Office for Other Bangsamoro Communities (OOBC)

## Quick Links

- [System Status](https://status.obc.barmm.gov.ph)
- [API Documentation](https://api.obc.barmm.gov.ph/docs)
- [Training Materials](training/README.md)
- [Change Log](CHANGELOG.md)
- [Security Policy](SECURITY.md)
