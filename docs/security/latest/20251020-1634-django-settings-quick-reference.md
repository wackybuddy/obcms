# Django Settings Security - Quick Reference Card

**Print this page and keep it handy during deployment**

---

## Generate Secrets

```bash
# Generate all secrets at once
./scripts/setup/generate_secrets.sh

# Generate individual secrets
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
openssl rand -base64 32  # For passwords
openssl rand -hex 32     # For tokens
```

---

## Validate Settings

```bash
# Check security configuration
cd src && python manage.py check_security_settings

# Check deployment readiness
cd src && python manage.py check --deploy
```

---

## Required Environment Variables (Production)

```bash
# CRITICAL - Must be set
SECRET_KEY=<50+ character random string>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# RECOMMENDED - Should be set
ADMIN_URL=<unpredictable-path>/
SESSION_COOKIE_NAME=obcms_sessionid
REDIS_PASSWORD=<32+ character password>
POSTGRES_PASSWORD=<32+ character password>
METRICS_TOKEN=<64 hex character token>

# OPTIONAL - Enhance security
ADMIN_IP_WHITELIST=192.168.1.100,10.0.0.0/24
DB_SSLMODE=require
```

---

## Security Headers (Automatic in Production)

- ✅ HSTS: 1 year, includeSubDomains, preload
- ✅ SSL Redirect: All HTTP → HTTPS
- ✅ Content-Type Nosniff
- ✅ X-Frame-Options: DENY
- ✅ Referrer-Policy: strict-origin-when-cross-origin
- ✅ Permissions-Policy: Restricts camera, microphone, geolocation, etc.

---

## Session Security (Production)

- **Timeout:** 8 hours (28800 seconds)
- **SameSite:** Strict
- **HttpOnly:** True
- **Secure:** True (HTTPS only)
- **Extends on activity:** Yes

---

## Common Commands

```bash
# Start development server
cd src && python manage.py runserver

# Check for issues
cd src && python manage.py check

# Check security
cd src && python manage.py check_security_settings

# Check deployment readiness
cd src && python manage.py check --deploy

# Generate secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Run migrations
cd src && python manage.py migrate

# Collect static files
cd src && python manage.py collectstatic --noinput
```

---

## Troubleshooting

### Error: "SECRET_KEY is not set"
```bash
# Generate and add to .env
./scripts/setup/generate_secrets.sh
echo "SECRET_KEY=<generated-key>" >> .env
```

### Error: "SECRET_KEY must be at least 50 characters"
```bash
# Generate longer key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Error: "ALLOWED_HOSTS must be explicitly set"
```bash
# Add to .env
echo "ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com" >> .env
```

### Error: "CSRF_TRUSTED_ORIGINS must be set"
```bash
# Add to .env (MUST include https://)
echo "CSRF_TRUSTED_ORIGINS=https://yourdomain.com" >> .env
```

### Warning: "SESSION_COOKIE_SECURE should be True"
**Normal in development** - Requires HTTPS in production

### Warning: "ADMIN_IP_WHITELIST is empty"
```bash
# Add to .env (production only)
echo "ADMIN_IP_WHITELIST=192.168.1.100,10.0.0.0/24" >> .env
```

---

## Secret Rotation Schedule

| Secret | Frequency | Priority |
|--------|-----------|----------|
| SECRET_KEY | Annually | HIGH |
| Database passwords | Quarterly | HIGH |
| Redis password | Quarterly | MEDIUM |
| API tokens | Monthly | MEDIUM |
| METRICS_TOKEN | Quarterly | LOW |

---

## Pre-Deployment Checklist

- [ ] Generate production secrets
- [ ] Set SECRET_KEY (50+ characters)
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Configure CSRF_TRUSTED_ORIGINS (with https://)
- [ ] Set unique ADMIN_URL
- [ ] Set Redis password
- [ ] Set database password
- [ ] Set METRICS_TOKEN
- [ ] Configure ADMIN_IP_WHITELIST
- [ ] Run: `python manage.py check_security_settings`
- [ ] Run: `python manage.py check --deploy`
- [ ] Test in staging first

---

## Documentation

- **Full Guide:** `docs/security/DJANGO_SETTINGS_SECURITY.md`
- **Implementation:** `docs/security/DJANGO_SETTINGS_SECURITY_IMPLEMENTATION_SUMMARY.md`
- **Audit Checklist:** `docs/security/SECURITY_AUDIT_CHECKLIST.md`

---

## Support

**Security Issues:** security@oobc.gov.ph
**Documentation:** See `CLAUDE.md`

---

**Version:** 1.0 | **Updated:** October 20, 2025
