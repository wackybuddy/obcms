"""
OBCMS Django Application Initialization.

This module ensures Celery is loaded when Django starts so that
shared_task decorators will use the Celery app instance.
"""

# Load Celery app on Django startup
# This ensures that @shared_task decorator will use this app
from .celery import app as celery_app

__all__ = ('celery_app',)
