# Django Settings Security Guide

## Pre-Deployment Security Checklist

Before deploying to production, verify ALL of these settings:

### 1. SECRET_KEY ✅
- [ ] Unique per environment
- [ ] At least 50 characters
- [ ] Cryptographically secure
- [ ] Never committed to git
- [ ] Stored in environment variable

**Generate:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. DEBUG ✅
- [ ] Set to `False` in production
- [ ] Validated in production.py

### 3. ALLOWED_HOSTS ✅
- [ ] Configured with actual domain names
- [ ] Not using `*` wildcard
- [ ] Includes all production domains

### 4. Session Security ✅
- [ ] `SESSION_COOKIE_SECURE = True` (HTTPS only)
- [ ] `SESSION_COOKIE_HTTPONLY = True`
- [ ] `SESSION_COOKIE_SAMESITE = "Strict"`
- [ ] `SESSION_COOKIE_AGE = 28800` (8 hours)
- [ ] Custom `SESSION_COOKIE_NAME` set

### 5. CSRF Protection ✅
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SAMESITE = "Strict"`
- [ ] `CSRF_TRUSTED_ORIGINS` configured with https:// scheme

### 6. Admin URL ✅
- [ ] Changed from default `/admin/`
- [ ] Uses unpredictable path
- [ ] Set via `ADMIN_URL` environment variable

### 7. IP Whitelist ✅
- [ ] `ADMIN_IP_WHITELIST` configured
- [ ] Contains authorized IP addresses

### 8. Metrics Authentication ✅
- [ ] `METRICS_TOKEN` generated and set
- [ ] Token at least 32 characters

## Validation Command

Run security settings check:
```bash
cd src
python manage.py check_security_settings
```

Expected output:
```
✅ All security settings validated

==================================================
Total Errors: 0
Total Warnings: 0
==================================================
✅ Security check PASSED
```

## Django Deployment Check

Run Django's built-in deployment check:
```bash
cd src
python manage.py check --deploy
```

This checks for common deployment issues and security misconfigurations.

## Security Headers Enabled

The following security headers are automatically configured in production:

- ✅ **HSTS** (HTTP Strict Transport Security)
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
  - Forces HTTPS for 1 year

- ✅ **SSL Redirect**
  - All HTTP requests automatically redirect to HTTPS

- ✅ **Content-Type Nosniff**
  - `X-Content-Type-Options: nosniff`
  - Prevents MIME type sniffing

- ✅ **X-Frame-Options**
  - `X-Frame-Options: DENY`
  - Prevents clickjacking attacks

- ✅ **Referrer Policy**
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - Controls referrer information

- ✅ **Permissions Policy**
  - Restricts browser features (camera, microphone, geolocation, etc.)

## Secrets Management

### Development

Use `.env` file (never commit):
```bash
# Copy template
cp .env.example .env

# Generate secrets
./scripts/setup/generate_secrets.sh

# Edit .env with generated values
nano .env
```

### Production

**Option 1: Environment Variables (Recommended)**
```bash
# Set via Docker/Coolify environment variables
# Never store in docker-compose.yml
```

**Option 2: Secrets Management Service**
- AWS Secrets Manager
- HashiCorp Vault
- Docker Secrets
- Kubernetes Secrets

### Secret Rotation Schedule

| Secret | Rotation Frequency | Priority |
|--------|-------------------|----------|
| SECRET_KEY | Annually | HIGH |
| Database passwords | Quarterly | HIGH |
| Redis password | Quarterly | MEDIUM |
| API tokens | Monthly | MEDIUM |
| METRICS_TOKEN | Quarterly | LOW |

## Configuration Files Security

### Files Modified

1. **`src/obc_management/settings/base.py`**
   - Removed insecure SECRET_KEY default
   - Added SECRET_KEY validation (length, format)

2. **`src/obc_management/settings/production.py`**
   - Added strict SECRET_KEY validation
   - Tightened session security (8-hour timeout)
   - Added security headers (HSTS, CSP, Permissions Policy)
   - Removed deprecated `SECURE_BROWSER_XSS_FILTER`

3. **`src/obc_management/urls.py`**
   - Made admin URL configurable via `ADMIN_URL` environment variable
   - Default: `admin/`
   - Production: Use unpredictable path (e.g., `secretadmin2024/`)

4. **`.env.example`**
   - Comprehensive security documentation
   - Security best practices checklist
   - Example values for all security settings

### New Files Created

1. **`scripts/setup/generate_secrets.sh`**
   - Generates cryptographically secure secrets
   - Provides SECRET_KEY, passwords, tokens

2. **`src/common/management/commands/check_security_settings.py`**
   - Validates security configuration
   - Reports errors and warnings
   - Exits with error code if issues found

3. **`docs/security/DJANGO_SETTINGS_SECURITY.md`**
   - This documentation file

## Testing Security Configuration

### 1. Test SECRET_KEY Validation

**Test: Missing SECRET_KEY**
```bash
# Remove SECRET_KEY from .env
cd src
python manage.py check
# Expected: ValueError: SECRET_KEY is not set
```

**Test: Short SECRET_KEY**
```bash
# Set SECRET_KEY=short in .env
cd src
python manage.py check
# Expected: ValueError: SECRET_KEY must be at least 50 characters
```

**Test: Insecure SECRET_KEY**
```bash
# Set SECRET_KEY=django-insecure-xxx in .env
cd src
python manage.py check
# Expected: ValueError: SECRET_KEY must not use the default insecure key
```

### 2. Test Production Settings

**Test: DEBUG=True in production**
```bash
# Set DEBUG=True in .env.production
DJANGO_SETTINGS_MODULE=obc_management.settings.production python manage.py check
# Expected: ValueError: DEBUG must be False in production
```

### 3. Test Admin URL Configuration

**Test: Custom admin URL**
```bash
# Set ADMIN_URL=customadmin123/ in .env
cd src
python manage.py runserver
# Visit: http://localhost:8000/customadmin123/
# Expected: Django admin login page
```

### 4. Run Security Validation

```bash
cd src
python manage.py check_security_settings
```

## Troubleshooting

### Error: "SECRET_KEY is not set"

**Cause:** `.env` file missing or SECRET_KEY not defined

**Solution:**
```bash
# Generate new SECRET_KEY
./scripts/setup/generate_secrets.sh

# Copy to .env
echo "SECRET_KEY=<generated-key>" >> .env
```

### Error: "ALLOWED_HOSTS must be explicitly set"

**Cause:** Production settings require explicit ALLOWED_HOSTS

**Solution:**
```bash
# Add to .env
echo "ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com" >> .env
```

### Error: "CSRF_TRUSTED_ORIGINS must be set"

**Cause:** Production requires CSRF trusted origins with https:// scheme

**Solution:**
```bash
# Add to .env (MUST include https://)
echo "CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com" >> .env
```

### Warning: "SESSION_COOKIE_AGE is 1209600s (>8 hours)"

**Cause:** Base settings use 2-week session timeout

**Solution:** Production settings override this to 8 hours automatically. No action needed.

### Warning: "ADMIN_IP_WHITELIST is empty"

**Cause:** Admin accessible from any IP address

**Solution (Production):**
```bash
# Add to .env
echo "ADMIN_IP_WHITELIST=192.168.1.100,10.0.0.0/24" >> .env
```

## Security Best Practices

### 1. Environment Separation

Use different secrets for each environment:

| Environment | SECRET_KEY | Database | Admin URL |
|-------------|-----------|----------|-----------|
| Development | dev-key-xxx | obcms_dev | admin/ |
| Staging | staging-key-xxx | obcms_staging | stagingadmin/ |
| Production | prod-key-xxx | obcms_prod | [unpredictable] |

### 2. Access Control

**Admin IP Whitelist:**
```bash
# Organization IP ranges only
ADMIN_IP_WHITELIST=203.177.12.0/24,10.0.0.0/8

# VPN IP range
ADMIN_IP_WHITELIST=192.168.100.0/24

# Specific IPs
ADMIN_IP_WHITELIST=203.177.12.45,192.168.1.100
```

### 3. Monitoring

**Enable audit logging:**
- All admin actions logged via `django-auditlog`
- Failed login attempts tracked via `django-axes`
- Security events logged to `logs/rbac_security.log`

**Review logs regularly:**
```bash
# Check security logs
tail -f src/logs/rbac_security.log

# Check failed login attempts
cd src
python manage.py axes_list_attempts
```

### 4. Regular Security Audits

**Schedule:**
- Weekly: Review security logs
- Monthly: Run security checks
- Quarterly: Rotate passwords
- Annually: Rotate SECRET_KEY

**Commands:**
```bash
# Security checks
cd src
python manage.py check_security_settings
python manage.py check --deploy

# Dependency vulnerabilities
pip-audit

# Update dependencies
pip install -r requirements/production.txt --upgrade
```

## References

- [Django Security Guide](https://docs.djangoproject.com/en/4.2/topics/security/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/)

## Support

For security questions or to report vulnerabilities:
- Email: security@oobc.gov.ph
- See: `docs/security/INCIDENT_RESPONSE_PLAYBOOK.md`
