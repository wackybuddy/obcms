"""
Development settings for OBCMS.

Use this for local development with additional debugging tools.
"""

from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)

# Less strict ALLOWED_HOSTS for development
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "0.0.0.0"])

# Development-specific apps
INSTALLED_APPS += [
    # Add development tools here if needed
    # 'debug_toolbar',
    # 'django_extensions',
]

# Development-specific middleware
# if 'debug_toolbar' in INSTALLED_APPS:
#     MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
#     INTERNAL_IPS = ['127.0.0.1']

# Email backend for development (console output)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable some security features in development for convenience
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# More verbose logging in development
LOGGING["root"]["level"] = "DEBUG"
LOGGING["loggers"]["django"]["level"] = "DEBUG"
