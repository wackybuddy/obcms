"""Celery tasks for MANA workflows (fallback to synchronous execution if Celery is absent)."""

from __future__ import annotations

try:
    from celery import shared_task
except ImportError:  # pragma: no cover

    def shared_task(*dargs, **dkwargs):  # type: ignore
        def decorator(func):
            setattr(func, "delay", func)
            return func

        if dargs and callable(dargs[0]):
            return decorator(dargs[0])
        return decorator


from django.contrib.auth import get_user_model

from .models import Assessment, WorkshopActivity
from .services.workshop_access import WorkshopAccessManager
from .services.workshop_synthesis import AIWorkshopSynthesizer

User = get_user_model()


@shared_task
def auto_unlock_due_workshops(assessment_id: str) -> int:
    """Background task to unlock workshops that have reached their schedule."""
    assessment = Assessment.objects.get(id=assessment_id)
    manager = WorkshopAccessManager(assessment)
    return manager.auto_unlock_due_workshops()


@shared_task
def generate_workshop_synthesis(
    workshop_id: int,
    filters: dict | None,
    created_by_id: int | None,
    provider: str = "anthropic",
    custom_prompt: str | None = None,
) -> dict:
    """Queueable task to run AI workshop synthesis."""
    workshop = WorkshopActivity.objects.get(id=workshop_id)
    created_by = User.objects.filter(id=created_by_id).first()

    synthesizer = AIWorkshopSynthesizer(workshop, filters)
    synthesis = synthesizer.synthesize(
        created_by=created_by,
        provider=provider,
        custom_prompt=custom_prompt,
    )

    return {
        "synthesis_id": synthesis.id,
        "status": synthesis.status,
    }
