#!/bin/bash
# Generate secure secrets for OBCMS deployment

echo "=========================================="
echo "OBCMS Security Secrets Generator"
echo "=========================================="
echo ""
echo "Copy these values to your .env file and keep them secure!"
echo "NEVER commit .env to version control!"
echo ""

# Generate SECRET_KEY
echo "SECRET_KEY (Django):"
# Try to use project's virtual environment if available
if [ -f "../venv/bin/python" ]; then
    ../venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
elif [ -f "../../venv/bin/python" ]; then
    ../../venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
else
    # Fallback: Generate using openssl (same randomness as Django)
    openssl rand -base64 50 | tr -d '\n' && echo
fi
echo ""

# Generate Redis password
echo "REDIS_PASSWORD:"
openssl rand -base64 32
echo ""

# Generate PostgreSQL password
echo "POSTGRES_PASSWORD:"
openssl rand -base64 32
echo ""

# Generate Metrics token
echo "METRICS_TOKEN:"
openssl rand -hex 32
echo ""

# Generate admin URL suggestion
echo "ADMIN_URL suggestion:"
echo "admin$(openssl rand -hex 8)/"
echo ""

echo "=========================================="
echo "Security Reminders:"
echo "=========================================="
echo "1. Store these secrets securely (use a password manager)"
echo "2. Never commit .env files to git"
echo "3. Use different secrets for each environment (dev/staging/prod)"
echo "4. Rotate secrets regularly (annually for SECRET_KEY, quarterly for passwords)"
echo "5. Use environment-specific admin URLs in production"
echo ""
echo "Next steps:"
echo "1. Copy the generated values above to your .env file"
echo "2. Update ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS"
echo "3. Run: cd src && python manage.py check_security_settings"
echo "4. Run: cd src && python manage.py check --deploy"
echo "=========================================="
