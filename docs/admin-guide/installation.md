# Installation Guide

This guide provides step-by-step instructions for installing the OBC Management System on a production server.

## System Requirements

### Hardware Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 100GB minimum, SSD recommended
- **Network**: Stable internet connection with adequate bandwidth

### Software Requirements
- **Operating System**: Ubuntu 20.04 LTS or later / CentOS 8 or later
- **Python**: 3.12 (pinned via version manager)
- **Database**: PostgreSQL 13 or later
- **Web Server**: Nginx 1.18 or later
- **SSL Certificate**: Let's Encrypt or commercial SSL certificate

## Pre-Installation Setup

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Packages
```bash
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip postgresql postgresql-contrib nginx git curl
```

> **Note:** If your distribution does not provide Python 3.12, install it from the [deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa) or with a version manager such as pyenv/asdf to match the pinned interpreter.

### 3. Create System User
```bash
sudo useradd --system --shell /bin/bash --home /var/www/obc-system --create-home obc
sudo usermod -aG www-data obc
```

### 4. Configure PostgreSQL
```bash
sudo -u postgres createuser --interactive
# Create user: obc_user
# Should the new role be a superuser? n
# Should the new role be allowed to create databases? y
# Should the new role be allowed to create more new roles? n

sudo -u postgres createdb obc_database --owner=obc_user
sudo -u postgres psql -c "ALTER USER obc_user PASSWORD 'secure_password_here';"
```

## Installation Steps

### 1. Clone Repository
```bash
sudo -u obc git clone https://github.com/oobc/obc-management-system.git /var/www/obc-system
cd /var/www/obc-system
```

### 2. Create Virtual Environment
```bash
sudo -u obc python3.12 -m venv venv
sudo -u obc /var/www/obc-system/venv/bin/pip install --upgrade pip
```

### 3. Install Python Dependencies
```bash
sudo -u obc /var/www/obc-system/venv/bin/pip install -r requirements/production.txt
```

### 4. Configure Environment Variables
```bash
sudo -u obc cp .env.example .env
sudo -u obc nano .env
```

Edit the `.env` file with your configuration:
```env
# Basic Configuration
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=obc.barmm.gov.ph,www.obc.barmm.gov.ph

# Database Configuration
DATABASE_URL=postgres://obc_user:secure_password_here@localhost:5432/obc_database

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@barmm.gov.ph
EMAIL_HOST_PASSWORD=your-email-password

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Cache Configuration (Redis)
REDIS_URL=redis://localhost:6379/0

# File Storage
MEDIA_ROOT=/var/www/obc-system/media
STATIC_ROOT=/var/www/obc-system/static
```

### 5. Run Database Migrations
```bash
cd /var/www/obc-system/src
sudo -u obc /var/www/obc-system/venv/bin/python manage.py migrate
```

### 6. Create Superuser
```bash
sudo -u obc /var/www/obc-system/venv/bin/python manage.py createsuperuser
```

### 7. Collect Static Files
```bash
sudo -u obc /var/www/obc-system/venv/bin/python manage.py collectstatic --noinput
```

### 8. Set Up File Permissions
```bash
sudo chown -R obc:www-data /var/www/obc-system
sudo chmod -R 755 /var/www/obc-system
sudo chmod -R 664 /var/www/obc-system/media
sudo chmod -R 664 /var/www/obc-system/static
```

## Service Configuration

### 1. Install Gunicorn Service
```bash
sudo cp /var/www/obc-system/deployment/systemd/obc-gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable obc-gunicorn
```

### 2. Create Log Directories
```bash
sudo mkdir -p /var/log/obc-system
sudo chown obc:www-data /var/log/obc-system
sudo mkdir -p /run/gunicorn
sudo chown obc:www-data /run/gunicorn
```

### 3. Configure Nginx
```bash
sudo cp /var/www/obc-system/deployment/nginx/obc-system.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/obc-system.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
```

### 4. Set Up SSL Certificate
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d obc.barmm.gov.ph -d www.obc.barmm.gov.ph
```

## Start Services

### 1. Start Gunicorn
```bash
sudo systemctl start obc-gunicorn
sudo systemctl status obc-gunicorn
```

### 2. Start Nginx
```bash
sudo systemctl restart nginx
sudo systemctl status nginx
```

## Post-Installation Setup

### 1. Test Installation
Visit your domain in a web browser and verify:
- [ ] Site loads without errors
- [ ] Admin interface is accessible
- [ ] Login functionality works
- [ ] Static files are served correctly

### 2. Set Up Backup System
```bash
sudo cp /var/www/obc-system/deployment/scripts/backup.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/backup.sh

# Add to crontab for daily backups
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup.sh
```

### 3. Configure Monitoring
```bash
# Install monitoring tools (optional)
sudo apt install htop iotop fail2ban
```

### 4. Set Up Firewall
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
```

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   sudo chown -R obc:www-data /var/www/obc-system
   sudo chmod -R 755 /var/www/obc-system
   ```

2. **Database Connection Issues**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check database credentials in `.env` file
   - Test connection: `sudo -u obc psql -h localhost -U obc_user -d obc_database`

3. **Static Files Not Loading**
   ```bash
   sudo -u obc /var/www/obc-system/venv/bin/python manage.py collectstatic --noinput
   sudo systemctl restart nginx
   ```

4. **Service Won't Start**
   ```bash
   sudo journalctl -u obc-gunicorn -n 50
   sudo systemctl status obc-gunicorn
   ```

### Log Locations
- **Application Logs**: `/var/log/obc-system/`
- **Nginx Logs**: `/var/log/nginx/`
- **System Logs**: `journalctl -u obc-gunicorn`

## Security Checklist

- [ ] SSL certificate installed and working
- [ ] Firewall configured and enabled
- [ ] Database access restricted to localhost
- [ ] Admin interface access restricted (optional)
- [ ] Regular security updates scheduled
- [ ] Backup system configured and tested
- [ ] Strong passwords for all accounts
- [ ] File permissions set correctly

## Next Steps

After successful installation:
1. Read the [Configuration Guide](configuration.md)
2. Set up user accounts and permissions
3. Configure backup and monitoring
4. Review the [User Guide](../user-guide/README.md)
5. Train your team on system usage
