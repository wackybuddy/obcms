"""Middleware utilities for MANA workshop routes."""

from __future__ import annotations

import uuid
from typing import Optional

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from .models import Assessment, WorkshopParticipantAccount


class ManaWorkshopContextMiddleware(MiddlewareMixin):
    """Attach assessment and participant context on workshop-specific routes."""

    def process_request(self, request):
        request.mana_assessment = getattr(request, "mana_assessment", None)
        request.mana_participant_account = getattr(
            request, "mana_participant_account", None
        )

        if not request.user.is_authenticated:
            return None

        path = request.path.strip("/")
        segments = path.split("/")

        if len(segments) < 4:
            return None

        if segments[0] != "mana" or segments[1] != "workshops" or segments[2] != "assessments":
            return None

        assessment_id = segments[3]
        try:
            assessment_uuid = uuid.UUID(assessment_id)
        except (ValueError, AttributeError):
            return None

        assessment = Assessment.objects.filter(id=assessment_uuid).first()
        if not assessment:
            return None

        request.mana_assessment = assessment

        if request.path.startswith("/mana/workshops/assessments/"):
            participant = WorkshopParticipantAccount.objects.filter(
                assessment=assessment,
                user=request.user,
            ).select_related("user").first()
            if participant:
                request.mana_participant_account = participant

        return None


class ManaParticipantAccessMiddleware(MiddlewareMixin):
    """Restrict non-staff MANA participants to allowed modules only."""

    ALLOWED_PATHS = {
        "/",
        "/dashboard/",
        "/profile/",
        "/mana/",
        "/logout/",
    }

    ALLOWED_PREFIXES = (
        "/mana/workshops/",  # New participant workshop system (sequential access)
        "/communities/manageprovincial",
        "/communities/province/",
        "/static/",
    )

    # Staff-only paths that participants should NOT access
    # /mana/regional/ - Legacy MANA system (OOBC staff only)
    # /mana/provincial/ - Provincial MANA (OOBC staff only)

    def process_request(self, request):
        user = getattr(request, "user", None)

        if (
            not user
            or not user.is_authenticated
            or user.is_staff
            or user.is_superuser
        ):
            return None

        if not user.has_perm("mana.can_access_regional_mana"):
            return None

        if user.has_perm("mana.can_facilitate_workshop"):
            return None

        path = request.path

        try:
            participant_account = user.workshop_participant_account
        except WorkshopParticipantAccount.DoesNotExist:
            return redirect("common:dashboard")

        onboarding_url = reverse(
            "mana:participant_onboarding",
            args=[participant_account.assessment_id],
        )

        if path == onboarding_url:
            return None

        if path == "/logout/":
            return None

        if path.startswith("/static/") or path.startswith("/media/"):
            return None

        if not participant_account.profile_completed or not participant_account.consent_given:
            return redirect(onboarding_url)

        if path in self.ALLOWED_PATHS or path.startswith(self.ALLOWED_PREFIXES):
            return None

        participant_dashboard = reverse("mana:participant_dashboard", args=[participant_account.assessment_id])
        return redirect(participant_dashboard)
