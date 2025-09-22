"""Test settings stripping optional third-party dependencies when offline."""

from .settings import *  # noqa: F401,F403

OPTIONAL_APPS = {
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "django_extensions",
    "crispy_forms",
}

INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in OPTIONAL_APPS]
MIDDLEWARE = [mw for mw in MIDDLEWARE if not mw.startswith("corsheaders.")]

# Ensure REST configuration doesn't reference missing modules
REST_FRAMEWORK = {}  # type: ignore
