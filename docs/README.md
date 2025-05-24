# OBC Management System Documentation

## Overview

The Other Bangsamoro Communities (OBC) Management System is a comprehensive web-based platform designed to support the Office for Other Bangsamoro Communities (OOBC) in managing and coordinating services for Bangsamoro communities outside the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM).

## Quick Start

### For Users
- [User Guide](user-guide/README.md) - Complete guide for end users
- [Getting Started](user-guide/getting-started.md) - Quick start tutorial
- [FAQ](user-guide/faq.md) - Frequently asked questions

### For Administrators
- [Administrator Guide](admin-guide/README.md) - System administration guide
- [Installation Guide](admin-guide/installation.md) - Server setup and installation
- [Configuration Guide](admin-guide/configuration.md) - System configuration options

### For Developers
- [Developer Guide](developer-guide/README.md) - Technical documentation
- [API Documentation](api/README.md) - API reference and examples
- [Contributing](CONTRIBUTING.md) - How to contribute to the project

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

## Key Features

- **Multi-level Geographic Support**: Region, Province, Municipality, Barangay hierarchy
- **Role-based Access Control**: Different user types with appropriate permissions
- **Comprehensive API**: RESTful API for integration and mobile applications
- **Data Import Tools**: CSV/Excel import with validation and mapping
- **Audit Trail**: Complete activity logging and user action tracking
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices
- **Security**: HTTPS, CSRF protection, SQL injection prevention
- **Scalability**: Designed to handle thousands of communities and users

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