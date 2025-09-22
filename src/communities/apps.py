from django.apps import AppConfig


class CommunitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "communities"

    def ready(self):
        # Import signal handlers
        from . import signals  # noqa: F401
