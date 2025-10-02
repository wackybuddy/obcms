"""
Settings package for OBCMS.

By default, imports from base settings.
Override with DJANGO_SETTINGS_MODULE environment variable:
- obc_management.settings (default - uses base)
- obc_management.settings.development
- obc_management.settings.production
"""

from .base import *  # noqa
