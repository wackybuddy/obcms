"""Shared serializer helpers for the communities app."""

from django.db import models as django_models

from ..models import CommunityProfileBase

COMMUNITY_PROFILE_SERIALIZER_FIELDS = [
    field.name
    for field in CommunityProfileBase._meta.get_fields()
    if isinstance(field, django_models.Field)
    and not field.auto_created
    and field.name not in {"created_at", "updated_at"}
]

__all__ = ["COMMUNITY_PROFILE_SERIALIZER_FIELDS"]
