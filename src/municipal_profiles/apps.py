from django.apps import AppConfig


class MunicipalProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "municipal_profiles"

    def ready(self):
        from . import signals  # noqa: F401
