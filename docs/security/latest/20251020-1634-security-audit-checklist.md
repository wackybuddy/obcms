# OBCMS Security Audit Implementation Checklist

**Audit Date:** October 20, 2025
**Status:** 🟡 IN PROGRESS
**Next Review:** January 20, 2026

Print this checklist and track progress manually, or use GitHub Issues to track each item.

---

## CRITICAL Priority (Week of Oct 20-27, 2025)

### Redis Server Security (CVE-2025-49844, CVE-2025-21605)

#### Development Environment
- [ ] Check Redis server version: `redis-cli INFO server | grep redis_version`
- [ ] Version is: _________________ (write version here)
- [ ] Is version 6.2.20+, 7.2.11+, 7.4.6+, 8.0.4+, or 8.2.2+? YES / NO
- [ ] If NO: Update Redis server (`brew upgrade redis` or `apt upgrade redis-server`)
- [ ] Enable Redis authentication in redis.conf
- [ ] Set strong Redis password
- [ ] Configure output buffer limits
- [ ] Restart Redis service
- [ ] Update CELERY_BROKER_URL with password in .env
- [ ] Update REDIS_URL with password in .env
- [ ] Test Redis authentication: `redis-cli -a PASSWORD PING`
- [ ] Test Celery connection with new password
- [ ] Test Django cache with new password

**Assigned To:** _______________________
**Completed Date:** _______________________
**Verified By:** _______________________

---

#### Production Environment
- [ ] SSH to production server
- [ ] Check Redis server version
- [ ] Version is: _________________ (write version here)
- [ ] Is version 6.2.20+, 7.2.11+, 7.4.6+, 8.0.4+, or 8.2.2+? YES / NO
- [ ] If NO: Update Redis server (Coolify/Docker/native)
- [ ] Enable Redis authentication in production redis.conf
- [ ] Set strong Redis password (different from dev)
- [ ] Configure output buffer limits
- [ ] Update production environment variables (CELERY_BROKER_URL, REDIS_URL)
- [ ] Restart Redis service
- [ ] Test Redis authentication
- [ ] Test Celery connection
- [ ] Test Django cache
- [ ] Monitor application for 24 hours after changes

**Assigned To:** _______________________
**Completed Date:** _______________________
**Verified By:** _______________________

---

### reportlab Security Configuration

#### Create Security Configuration
- [ ] Create file: `src/obc_management/reportlab_config.py`
- [ ] Add `configure_reportlab_security()` function
- [ ] Configure trusted_schemes (use ['data'] for highest security)
- [ ] If allowing external images: configure trusted_hosts
- [ ] Update `src/obc_management/__init__.py` to call configuration

**Assigned To:** _______________________
**Completed Date:** _______________________

---

#### Audit PDF Generation Code
- [ ] Review `src/mana/facilitator_views.py` line 30-31, 772
- [ ] Check if user-provided URLs are used: YES / NO
- [ ] Check if user-provided HTML is converted: YES / NO
- [ ] Review `src/communities/views.py` lines 20-24
- [ ] Check if user-provided URLs are used: YES / NO
- [ ] Check if user-provided HTML is converted: YES / NO
- [ ] Review `src/communities/data_utils.py` lines 18-22
- [ ] Check if user-provided URLs are used: YES / NO
- [ ] Check if user-provided HTML is converted: YES / NO
- [ ] Add URL validation if needed
- [ ] Add docstrings documenting security measures
- [ ] Test PDF generation still works
- [ ] Document any risks identified

**Assigned To:** _______________________
**Completed Date:** _______________________
**Verified By:** _______________________

---

### PyTorch Security Verification
- [x] ✅ COMPLETE - No torch.load() or torch.save() found in codebase
- [x] ✅ PyTorch used only via sentence-transformers (indirect)
- [x] ✅ No user-uploaded models processed
- [x] ✅ CVE-2025-32434 does not apply to OBCMS

**Status:** No action required
**Verified Date:** October 20, 2025

---

## HIGH Priority (Week of Oct 20-27, 2025)

### Testing After Critical Changes
- [ ] Run full test suite: `cd src && python manage.py test`
- [ ] All tests pass: YES / NO
- [ ] If NO, document failures: _______________________
- [ ] Run Django security check: `python manage.py check --deploy`
- [ ] All checks pass: YES / NO
- [ ] Test user login/logout
- [ ] Test PDF generation (communities, MANA reports)
- [ ] Test Celery tasks
- [ ] Test Redis caching
- [ ] Check application logs for errors
- [ ] Monitor for 48 hours after deployment

**Assigned To:** _______________________
**Completed Date:** _______________________

---

## MEDIUM Priority (Nov 1-30, 2025)

### Update Safe Minor Packages
- [ ] Backup current environment: `pip freeze > requirements/backup-2025-10-20.txt`
- [ ] Update psycopg: `pip install --upgrade "psycopg[binary]>=3.2.11"`
- [ ] Update google-ai-generativelanguage: `pip install --upgrade "google-ai-generativelanguage>=0.8.0"`
- [ ] Update grpcio-status: `pip install --upgrade "grpcio-status>=1.75.1"`
- [ ] Update iniconfig: `pip install --upgrade "iniconfig>=2.3.0"`
- [ ] Update pip: `pip install --upgrade pip`
- [ ] Run full test suite
- [ ] All tests pass: YES / NO
- [ ] Update requirements/base.txt with new versions
- [ ] Test in development for 1 week
- [ ] Deploy to staging
- [ ] Test in staging for 1 week
- [ ] Deploy to production

**Assigned To:** _______________________
**Target Completion:** November 15, 2025
**Completed Date:** _______________________

---

### Plan protobuf 6.x Migration
- [ ] Read breaking changes: https://protobuf.dev/news/v30/
- [ ] Document breaking changes that affect OBCMS
- [ ] Search for direct protobuf usage: `grep -rn "google.protobuf" src/`
- [ ] Create test branch: `git checkout -b feature/protobuf-6-migration`
- [ ] Update protobuf in test environment
- [ ] Run comprehensive tests
- [ ] Test Google Cloud integrations
- [ ] Document any issues found
- [ ] Create migration plan document
- [ ] Schedule migration for Q1 2026

**Assigned To:** _______________________
**Target Completion:** November 30, 2025 (planning only)
**Completed Date:** _______________________

---

### Update google-cloud-storage to 3.x
- [ ] Review changelog: https://github.com/googleapis/python-storage/releases
- [ ] Document breaking changes in 3.0.0
- [ ] Search for GCS usage: `grep -rn "google.cloud.storage" src/`
- [ ] List all files using GCS: _______________________
- [ ] Create test branch: `git checkout -b feature/gcs-3-migration`
- [ ] Update package: `pip install "google-cloud-storage>=3.4.1"`
- [ ] Run tests
- [ ] Test file upload/download functionality
- [ ] Deploy to development
- [ ] Test for 1 week
- [ ] Deploy to staging
- [ ] Test for 1 week
- [ ] Deploy to production

**Assigned To:** _______________________
**Target Completion:** December 15, 2025
**Completed Date:** _______________________

---

## LOW Priority (Dec 1-31, 2025)

### Verify axe-playwright-python License
- [ ] Check GitHub repository for license
- [ ] Repository URL: https://github.com/_______________________
- [ ] License found: _______________________
- [ ] Is license compatible? YES / NO
- [ ] If NO: Research alternative accessibility testing tools
- [ ] Document findings

**Assigned To:** _______________________
**Target Completion:** December 31, 2025
**Completed Date:** _______________________

---

## Continuous Monitoring Setup

### Install Security Tools
- [ ] Verify pip-audit installed: `pip show pip-audit`
- [ ] Add pip-audit to requirements/development.txt
- [ ] Create monthly audit script: `scripts/security-audit.sh`
- [ ] Make script executable: `chmod +x scripts/security-audit.sh`
- [ ] Test script runs successfully
- [ ] Schedule monthly execution (cron or manual reminder)

**Assigned To:** _______________________
**Completed Date:** _______________________

---

### Subscribe to Security Advisories
- [ ] Django Security: https://groups.google.com/g/django-announce
  - Subscribed by: _______________________
- [ ] PyTorch Security: https://github.com/pytorch/pytorch/security/advisories
  - Subscribed by: _______________________
- [ ] Redis Security: https://redis.io/blog/
  - Subscribed by: _______________________
- [ ] Python Security: https://github.com/pypa/advisory-database
  - Subscribed by: _______________________
- [ ] GitHub Dependabot: Enable for repository
  - Enabled: YES / NO
  - Enabled by: _______________________

**Assigned To:** _______________________
**Completed Date:** _______________________

---

## Django Settings Security Hardening (COMPLETED ✅)

### Configuration Security
- [x] ✅ Removed insecure default SECRET_KEY from base.py
- [x] ✅ Added SECRET_KEY validation (length >= 50 characters)
- [x] ✅ Added production SECRET_KEY validation in production.py
- [x] ✅ Tightened session security (8-hour timeout, Strict SameSite)
- [x] ✅ Made admin URL configurable via ADMIN_URL environment variable
- [x] ✅ Added security headers (Referrer-Policy, Permissions-Policy)
- [x] ✅ Removed deprecated SECURE_BROWSER_XSS_FILTER
- [x] ✅ Updated .env.example with comprehensive security documentation

### Security Tools Created
- [x] ✅ Created scripts/setup/generate_secrets.sh (secret generation)
- [x] ✅ Created check_security_settings management command
- [x] ✅ Created docs/security/DJANGO_SETTINGS_SECURITY.md

**Completed By:** Claude Code
**Completion Date:** October 20, 2025
**Files Modified:**
- src/obc_management/settings/base.py
- src/obc_management/settings/production.py
- src/obc_management/urls.py
- .env.example
- scripts/setup/generate_secrets.sh (new)
- src/common/management/commands/check_security_settings.py (new)
- docs/security/DJANGO_SETTINGS_SECURITY.md (new)

---

## Documentation Updates

### Update Security Documentation
- [x] ✅ Created DEPENDENCY_VULNERABILITY_AUDIT_REPORT.md
- [x] ✅ Created VULNERABILITY_AUDIT_EXECUTIVE_SUMMARY.md
- [x] ✅ Created VULNERABILITY_AUDIT_ACTION_PLAN.md
- [x] ✅ Created SECURITY_AUDIT_CHECKLIST.md
- [x] ✅ Created DJANGO_SETTINGS_SECURITY.md
- [ ] Update main security README (if exists)
- [ ] Add security audit to CI/CD pipeline
- [ ] Document Redis security configuration
- [ ] Document reportlab security configuration
- [ ] Update deployment documentation

**Assigned To:** _______________________
**Completed Date:** _______________________

---

## Final Verification

### Production Deployment Checklist
- [ ] All CRITICAL priority items completed
- [ ] All HIGH priority items completed
- [ ] Redis server updated and authenticated
- [ ] reportlab security configured
- [ ] pip-audit shows 0 vulnerabilities
- [ ] Tests pass in staging environment
- [ ] DEBUG=False in production settings
- [ ] SECRET_KEY is unique in production
- [ ] Database backups are current
- [ ] Rollback plan documented
- [ ] Team notified of changes
- [ ] Monitoring configured
- [ ] Documentation updated

**Deployment Date:** _______________________
**Deployed By:** _______________________
**Verified By:** _______________________

---

### Post-Deployment Monitoring (First 48 Hours)
- [ ] Hour 1: Check application logs
- [ ] Hour 2: Check Celery worker logs
- [ ] Hour 4: Check Redis connection stability
- [ ] Hour 8: Check PDF generation works
- [ ] Hour 24: Review error logs
- [ ] Hour 48: Confirm no issues
- [ ] Issues found: _______________________

**Monitored By:** _______________________

---

## Monthly Security Audit (Recurring)

### Next Audit Due: January 20, 2026

- [ ] Run pip-audit on all requirements
- [ ] Check for outdated packages
- [ ] Review security advisories for dependencies
- [ ] Check Redis server is still patched
- [ ] Verify reportlab security is configured
- [ ] Review application logs for security issues
- [ ] Update this checklist for next audit
- [ ] Document any new vulnerabilities found

**Completed By:** _______________________
**Completion Date:** _______________________

---

## Notes & Issues

Use this space to document any issues, blockers, or important notes:

```
Date: _______________________
Note: _______________________________________________________________
____________________________________________________________________
____________________________________________________________________

Date: _______________________
Note: _______________________________________________________________
____________________________________________________________________
____________________________________________________________________

Date: _______________________
Note: _______________________________________________________________
____________________________________________________________________
____________________________________________________________________
```

---

## Sign-off

### Development Environment
**CRITICAL items completed by:** _______________________
**Signature:** _______________________
**Date:** _______________________

### Production Environment
**All items reviewed by:** _______________________
**Signature:** _______________________
**Date:** _______________________

**Final approval by:** _______________________
**Signature:** _______________________
**Date:** _______________________

---

**Document Version:** 1.0
**Last Updated:** October 20, 2025
**Next Update:** After implementation or January 20, 2026
