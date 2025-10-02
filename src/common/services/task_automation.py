"""Task automation service for creating tasks from templates."""

from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


def create_tasks_from_template(template_name, **kwargs):
    """
    Create task set from template.

    Args:
        template_name: Name of TaskTemplate
        **kwargs: Domain-specific FK values (e.g., related_assessment=assessment_obj)
                 Also accepts: start_date, created_by

    Returns:
        List of created StaffTask objects
    """
    from common.models import StaffTask, TaskTemplate
    from common.services.resource_bookings import (
        create_bookings_for_task,
        ResourceBookingSpecError,
    )

    try:
        template = TaskTemplate.objects.get(name=template_name, is_active=True)
    except TaskTemplate.DoesNotExist:
        return []

    created_tasks = []
    base_date = kwargs.pop("start_date", None) or timezone.now().date()
    resource_booking_specs = kwargs.pop("resource_bookings", None)
    idempotency_filter = kwargs.pop("idempotency_filter", None)
    auto_generated = kwargs.pop("auto_generated", False)
    if isinstance(base_date, str):
        try:
            base_date = datetime.fromisoformat(base_date).date()
        except ValueError:
            base_date = timezone.now().date()
    created_by = kwargs.pop("created_by", None)

    # Extract template variable context
    context = {}
    for key, value in kwargs.items():
        if isinstance(value, str):
            context[key.replace("related_", "").replace("linked_", "")] = value
        elif hasattr(value, "__str__"):
            context[key.replace("related_", "").replace("linked_", "")] = str(value)

    task_field_names = {
        field.name
        for field in StaffTask._meta.get_fields()
        if getattr(field, "concrete", False)
    }
    task_kwargs = {
        key: value for key, value in kwargs.items() if key in task_field_names
    }

    if idempotency_filter:
        existing = StaffTask.objects.filter(
            created_from_template=template,
            **idempotency_filter,
        ).order_by("created_at")
        if existing.exists():
            return list(existing)

    for item in template.items.all():
        # Format title and description with context
        try:
            title = item.title.format(**context)
            description = item.description.format(**context)
        except (KeyError, ValueError):
            title = item.title
            description = item.description

        task = StaffTask.objects.create(
            title=title,
            description=description,
            priority=item.priority,
            status=StaffTask.STATUS_NOT_STARTED,
            domain=template.domain,
            task_category=item.task_category,
            estimated_hours=item.estimated_hours,
            due_date=base_date + timedelta(days=item.days_from_start),
            created_from_template=template,
            created_by=created_by,
            auto_generated=auto_generated,
            # Domain-specific fields
            assessment_phase=item.assessment_phase,
            policy_phase=item.policy_phase,
            service_phase=item.service_phase,
            task_role=item.task_role,
            **task_kwargs,
        )
        created_tasks.append(task)

        if resource_booking_specs:
            try:
                specs_to_apply = None
                if isinstance(resource_booking_specs, dict):
                    specs_to_apply = resource_booking_specs.get(item.sequence)
                    if specs_to_apply is None:
                        specs_to_apply = resource_booking_specs.get(item.title)
                    if specs_to_apply is None:
                        specs_to_apply = resource_booking_specs.get("default")
                else:
                    specs_to_apply = resource_booking_specs

                if specs_to_apply:
                    create_bookings_for_task(
                        task,
                        specs_to_apply,
                        user=created_by,
                    )
            except (ResourceBookingSpecError, ValidationError) as exc:
                # Bubble up with contextual information for troubleshooting
                raise ValidationError(
                    {
                        "resource_bookings": f"Failed to create resource booking for task '{title}': {exc}"
                    }
                ) from exc

    return created_tasks


# ========== SIGNAL HANDLERS FOR AUTOMATED TASK GENERATION ==========


@receiver(post_save, sender="mana.Assessment")
def create_assessment_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when MANA Assessment created."""
    if not created:
        return

    from common.models import TaskTemplate

    template_map = {
        "desk_review": "mana_assessment_desk_review",
        "survey": "mana_assessment_survey",
        "kii": "mana_assessment_kii",
        "workshop": "mana_assessment_workshop",
        "participatory": "mana_assessment_participatory",
        "observation": "mana_assessment_observation",
        "mixed": "mana_assessment_full_cycle",
    }

    methodology = getattr(instance, "primary_methodology", None)
    template_name = template_map.get(methodology, "mana_assessment_basic")
    if not TaskTemplate.objects.filter(name=template_name, is_active=True).exists():
        template_name = "mana_assessment_basic"
    start_date = (
        getattr(instance, "planned_start_date", None)
        or getattr(instance, "actual_start_date", None)
        or timezone.now().date()
    )

    create_tasks_from_template(
        template_name=template_name,
        related_assessment=instance,
        assessment_name=instance.title,
        start_date=start_date,
        created_by=getattr(instance, "created_by", None),
    )


@receiver(post_save, sender="mana.BaselineStudy")
def create_baseline_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when Baseline Study created."""
    if not created:
        return

    create_tasks_from_template(
        template_name="mana_baseline_study",
        related_baseline=instance,
        baseline_name=instance.title,
        start_date=(
            getattr(instance, "planned_start_date", None)
            or getattr(instance, "actual_start_date", None)
            or timezone.now().date()
        ),
        created_by=getattr(instance, "created_by", None),
    )


@receiver(post_save, sender="mana.WorkshopActivity")
def create_workshop_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when Workshop Activity created."""
    if not created:
        return

    create_tasks_from_template(
        template_name="mana_workshop_facilitation",
        related_workshop=instance,
        workshop_name=instance.title,
        start_date=getattr(instance, "scheduled_date", timezone.now().date()),
        created_by=getattr(instance, "created_by", None),
    )


@receiver(post_save, sender="coordination.Event")
def create_event_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when Event created."""
    if not created or instance.event_type not in ["meeting", "workshop", "conference"]:
        return

    template_map = {
        "meeting": "event_meeting_standard",
        "workshop": "event_workshop_full",
        "conference": "event_conference_full",
    }

    template_name = template_map.get(instance.event_type, "event_basic")

    create_tasks_from_template(
        template_name=template_name,
        linked_event=instance,
        event_name=instance.title,
        start_date=instance.start_date or timezone.now().date(),
        created_by=getattr(instance, "created_by", None),
    )


@receiver(post_save, sender="coordination.Partnership")
def create_partnership_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when Partnership created."""
    if not created:
        return

    lead_org = getattr(instance, "lead_organization", None)
    partnership_name = (
        f"Partnership with {lead_org.name}" if lead_org else instance.title
    )
    start_date = getattr(instance, "start_date", None) or timezone.now().date()

    create_tasks_from_template(
        template_name="partnership_negotiation",
        related_partnership=instance,
        partnership_name=partnership_name,
        start_date=start_date,
        created_by=getattr(instance, "created_by", None),
    )


@receiver(post_save, sender="policy_tracking.PolicyRecommendation")
def create_policy_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when Policy created."""
    if not created:
        return

    create_tasks_from_template(
        template_name="policy_development_full_cycle",
        related_policy=instance,
        policy_title=instance.title,
        start_date=timezone.now().date(),
        created_by=getattr(instance, "proposed_by", None),
    )


@receiver(post_save, sender="policy_tracking.PolicyImplementationMilestone")
def create_milestone_tasks(sender, instance, created, **kwargs):
    """Auto-create task when PolicyImplementationMilestone created."""
    if not created:
        return

    from common.models import StaffTask

    StaffTask.objects.create(
        title=f"Complete: {instance.title}",
        description=instance.description,
        related_policy=instance.policy,
        related_policy_milestone=instance,
        domain=StaffTask.DOMAIN_POLICY,
        policy_phase=StaffTask.POLICY_PHASE_IMPLEMENTATION,
        priority=(
            StaffTask.PRIORITY_HIGH
            if getattr(instance, "is_critical", False)
            else StaffTask.PRIORITY_MEDIUM
        ),
        due_date=instance.target_date,
        status=StaffTask.STATUS_NOT_STARTED,
    )


@receiver(post_save, sender="monitoring.MonitoringEntry")
def create_ppa_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when PPA created."""
    if not created or instance.category not in ["moa_ppa", "oobc_ppa"]:
        return

    create_tasks_from_template(
        template_name="ppa_budget_cycle",
        related_ppa=instance,
        ppa_title=instance.title,
        start_date=instance.start_date or timezone.now().date(),
        created_by=getattr(instance, "created_by", None),
    )


@receiver(post_save, sender="services.ServiceApplication")
def create_application_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when ServiceApplication submitted."""
    if not created or instance.status != "submitted":
        return

    from common.models import StaffTask

    StaffTask.objects.create(
        title=f"Review application: {instance.applicant_name}",
        description=f"Review service application for {instance.service.title}",
        related_service=instance.service,
        related_application=instance,
        domain=StaffTask.DOMAIN_SERVICES,
        service_phase=StaffTask.SERVICE_PHASE_REVIEW,
        priority=StaffTask.PRIORITY_MEDIUM,
        due_date=timezone.now().date() + timedelta(days=7),
        status=StaffTask.STATUS_NOT_STARTED,
    )
