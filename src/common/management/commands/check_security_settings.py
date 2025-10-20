"""Management command to validate security settings."""
from django.core.management.base import BaseCommand
from django.conf import settings
import sys


class Command(BaseCommand):
    """Check security configuration for production deployment."""

    help = 'Validate security settings for production deployment'

    def handle(self, *args, **options):
        """Run security checks."""
        errors = []
        warnings = []

        # Check DEBUG mode
        if settings.DEBUG:
            errors.append("DEBUG must be False in production")

        # Check SECRET_KEY
        if not settings.SECRET_KEY:
            errors.append("SECRET_KEY is not set")
        elif len(settings.SECRET_KEY) < 50:
            errors.append("SECRET_KEY must be at least 50 characters")
        elif settings.SECRET_KEY.startswith('django-insecure'):
            errors.append("SECRET_KEY uses insecure default")

        # Check ALLOWED_HOSTS
        if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
            errors.append("ALLOWED_HOSTS must be configured (not * or empty)")

        # Check session security
        if not settings.SESSION_COOKIE_SECURE:
            warnings.append("SESSION_COOKIE_SECURE should be True (requires HTTPS)")

        if not settings.CSRF_COOKIE_SECURE:
            warnings.append("CSRF_COOKIE_SECURE should be True (requires HTTPS)")

        if settings.SESSION_COOKIE_AGE > 28800:  # 8 hours
            warnings.append(f"SESSION_COOKIE_AGE is {settings.SESSION_COOKIE_AGE}s (>8 hours)")

        # Check Redis password
        redis_url = getattr(settings, 'REDIS_URL', '')
        if redis_url and ':@' in redis_url:
            errors.append("REDIS_URL missing password (found empty password)")

        # Check admin IP whitelist
        admin_whitelist = getattr(settings, 'ADMIN_IP_WHITELIST', [])
        if not admin_whitelist:
            warnings.append("ADMIN_IP_WHITELIST is empty (admin accessible from any IP)")

        # Check metrics authentication
        metrics_token = getattr(settings, 'METRICS_TOKEN', '')
        if not metrics_token:
            warnings.append("METRICS_TOKEN not set (metrics endpoint unprotected)")

        # Check CSRF trusted origins
        csrf_trusted = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
        if not csrf_trusted:
            warnings.append("CSRF_TRUSTED_ORIGINS not configured (may cause CSRF errors)")

        # Check security headers
        if not getattr(settings, 'SECURE_HSTS_SECONDS', 0):
            warnings.append("SECURE_HSTS_SECONDS not set (HSTS disabled)")

        if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
            warnings.append("SECURE_SSL_REDIRECT not enabled (HTTP not redirected to HTTPS)")

        # Check session cookie name
        if settings.SESSION_COOKIE_NAME == 'sessionid':
            warnings.append("SESSION_COOKIE_NAME uses default value (consider custom name)")

        # Print results
        if errors:
            self.stdout.write(self.style.ERROR('\n❌ SECURITY ERRORS (must fix):'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))

        if warnings:
            self.stdout.write(self.style.WARNING('\n⚠️  SECURITY WARNINGS (recommended):'))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f'  - {warning}'))

        if not errors and not warnings:
            self.stdout.write(self.style.SUCCESS('\n✅ All security settings validated'))

        # Print summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Total Errors: {len(errors)}')
        self.stdout.write(f'Total Warnings: {len(warnings)}')
        self.stdout.write('='*50 + '\n')

        if errors:
            self.stdout.write(self.style.ERROR('❌ Security check FAILED - fix errors before deployment'))
        elif warnings:
            self.stdout.write(self.style.WARNING('⚠️  Security check PASSED with warnings - review recommendations'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Security check PASSED'))

        # Exit with error code if errors found
        if errors:
            sys.exit(1)
