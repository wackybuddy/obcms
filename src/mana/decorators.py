"""Access control helpers for Regional MANA workshops."""

from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Assessment, WorkshopParticipantAccount


def facilitator_required(view_func):
    """Ensure the user has facilitator permissions for MANA workshops."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied

        if not (
            request.user.has_perm("mana.can_facilitate_workshop")
            or request.user.has_perm("mana.can_access_regional_mana")
            or request.user.is_staff
        ):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped


def participant_required(view_func):
    """Attach the participant account for the requested assessment to the request."""

    @wraps(view_func)
    def _wrapped(request, assessment_id, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied

        assessment = get_object_or_404(Assessment, pk=assessment_id)
        try:
            account = WorkshopParticipantAccount.objects.select_related("user").get(
                assessment=assessment,
                user=request.user,
            )
        except WorkshopParticipantAccount.DoesNotExist as exc:
            raise PermissionDenied from exc

        # Attach for downstream use
        request.mana_assessment = assessment
        request.mana_participant_account = account
        return view_func(request, assessment_id, *args, **kwargs)

    return _wrapped
