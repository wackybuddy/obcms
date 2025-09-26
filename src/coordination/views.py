"""Frontend views for the coordination module."""

import json
import logging
from datetime import datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .forms import (
    EventForm,
    OrganizationContactFormSet,
    OrganizationForm,
    PartnershipDocumentFormSet,
    PartnershipForm,
    PartnershipMilestoneFormSet,
    PartnershipSignatoryFormSet,
    StakeholderEngagementForm,
)
from .models import Event, Organization, Partnership, StakeholderEngagement


logger = logging.getLogger(__name__)


def _organization_form(request, organization_id=None):
    """Shared create/update handler for organization form flow."""

    organization_id = (
        organization_id
        or request.GET.get("organization")
        or request.POST.get("organization_id")
    )
    is_edit = bool(organization_id)
    organization = None

    if is_edit:
        organization = get_object_or_404(Organization, pk=organization_id)
        if not request.user.has_perm("coordination.change_organization"):
            raise PermissionDenied
    else:
        if not request.user.has_perm("coordination.add_organization"):
            raise PermissionDenied

    form_instance = organization or Organization(created_by=request.user)

    if request.method == "POST":
        form_kwargs = {"instance": organization} if is_edit else {}
        form = OrganizationForm(request.POST, **form_kwargs)
        formset = OrganizationContactFormSet(
            request.POST,
            instance=form_instance,
            prefix="contacts",
        )

        if form.is_valid() and formset.is_valid():
            saved_organization = form.save(commit=False)
            if not is_edit:
                saved_organization.created_by = request.user
            saved_organization.save()
            formset.instance = saved_organization
            formset.save()
            if is_edit:
                messages.success(request, "Organization successfully updated.")
                return redirect(
                    "common:coordination_organization_detail",
                    organization_id=saved_organization.pk,
                )
            messages.success(request, "Organization successfully created.")
            return redirect("common:coordination_organizations")
        messages.error(request, "Please correct the errors below before submitting.")
        if form.errors:
            logger.warning("Organization form errors: %s", form.errors)
        if formset.errors or formset.non_form_errors():
            logger.warning(
                "Organization contact formset errors: %s | non-form: %s",
                formset.errors,
                formset.non_form_errors(),
            )
    else:
        form_kwargs = {"instance": organization} if is_edit else {}
        form = OrganizationForm(**form_kwargs)
        formset = OrganizationContactFormSet(
            instance=form_instance,
            prefix="contacts",
        )

    context = {
        "form": form,
        "formset": formset,
        "return_url": reverse("common:coordination_organizations"),
        "is_edit": is_edit,
        "organization": organization,
    }
    return render(request, "coordination/organization_form.html", context)


@login_required
def organization_create(request):
    """Render and process the frontend organization creation form."""

    return _organization_form(request)


@login_required
def organization_edit(request, organization_id):
    """Render and process the frontend organization edit form."""

    return _organization_form(request, organization_id=organization_id)


@login_required
def organization_detail(request, organization_id):
    """Display organization details in the frontend directory."""

    organization = get_object_or_404(
        Organization.objects.select_related("created_by").prefetch_related(
            "contacts",
            "led_partnerships__lead_organization",
            "partnerships__lead_organization",
        ),
        pk=organization_id,
    )

    led_partnerships = list(organization.led_partnerships.all())
    led_partnership_ids = {partnership.pk for partnership in led_partnerships}
    member_partnerships = [
        partnership
        for partnership in organization.partnerships.all()
        if partnership.pk not in led_partnership_ids
    ]
    contacts = list(organization.contacts.all())
    total_partnerships = len(led_partnerships) + len(member_partnerships)

    context = {
        "organization": organization,
        "contacts": contacts,
        "led_partnerships": led_partnerships,
        "member_partnerships": member_partnerships,
        "return_url": reverse("common:coordination_organizations"),
        "total_partnerships": total_partnerships,
    }
    return render(request, "coordination/organization_detail.html", context)


@login_required
def organization_delete(request, organization_id):
    """Handle deletion of an organization from the frontend UI."""

    organization = get_object_or_404(Organization, pk=organization_id)

    if not request.user.has_perm("coordination.delete_organization"):
        raise PermissionDenied

    if request.method == "POST":
        try:
            organization.delete()
        except ProtectedError as error:
            logger.warning(
                "Failed to delete organization %s due to protected relations: %s",
                organization.pk,
                error,
            )
            messages.error(
                request,
                "Unable to delete this organization because it is referenced by other records.",
            )
            return redirect(
                "common:coordination_organization_detail",
                organization_id=organization.pk,
            )
        messages.success(request, "Organization successfully deleted.")
        return redirect("common:coordination_organizations")

    context = {
        "organization": organization,
        "return_url": reverse("common:coordination_organizations"),
    }
    return render(request, "coordination/organization_confirm_delete.html", context)


@login_required
def partnership_create(request):
    """Render and process the frontend partnership creation form."""

    if not request.user.has_perm("coordination.add_partnership"):
        raise PermissionDenied

    partnership_instance = Partnership(created_by=request.user)

    if request.method == "POST":
        form = PartnershipForm(request.POST, request.FILES)
        signatory_formset = PartnershipSignatoryFormSet(
            request.POST,
            instance=partnership_instance,
            prefix="signatories",
        )
        milestone_formset = PartnershipMilestoneFormSet(
            request.POST,
            instance=partnership_instance,
            prefix="milestones",
        )
        document_formset = PartnershipDocumentFormSet(
            request.POST,
            request.FILES,
            instance=partnership_instance,
            prefix="documents",
        )

        if (
            form.is_valid()
            and signatory_formset.is_valid()
            and milestone_formset.is_valid()
            and document_formset.is_valid()
        ):
            partnership = form.save(commit=False)
            partnership.created_by = request.user
            partnership.save()
            if hasattr(form, "save_m2m"):
                form.save_m2m()

            signatory_formset.instance = partnership
            milestone_formset.instance = partnership
            document_formset.instance = partnership

            signatory_formset.save()
            milestone_formset.save()
            document_formset.save()

            messages.success(request, "Partnership successfully created.")
            return redirect("common:coordination_partnerships")
    else:
        form = PartnershipForm()
        signatory_formset = PartnershipSignatoryFormSet(
            instance=partnership_instance,
            prefix="signatories",
        )
        milestone_formset = PartnershipMilestoneFormSet(
            instance=partnership_instance,
            prefix="milestones",
        )
        document_formset = PartnershipDocumentFormSet(
            instance=partnership_instance,
            prefix="documents",
        )

    context = {
        "form": form,
        "signatory_formset": signatory_formset,
        "milestone_formset": milestone_formset,
        "document_formset": document_formset,
        "return_url": reverse("common:coordination_partnerships"),
        "page_title": "Create Partnership",
        "breadcrumb_label": "Create Partnership",
        "page_heading": "New Partnership Agreement",
        "submit_label": "Create partnership",
        "is_edit": False,
    }
    return render(request, "coordination/partnership_form.html", context)


@login_required
def partnership_detail(request, partnership_id):
    """Render a partnership summary mirroring community detail views."""

    partnership = get_object_or_404(
        Partnership.objects.select_related(
            "lead_organization",
            "focal_person",
            "backup_focal_person",
            "created_by",
        )
        .prefetch_related(
            "organizations",
            "communities",
            "signatories__organization",
            "milestones",
            "documents",
        ),
        pk=partnership_id,
    )

    signatories = partnership.signatories.select_related("organization").all()
    milestones = partnership.milestones.all()
    documents = partnership.documents.all()

    context = {
        "partnership": partnership,
        "signatories": signatories,
        "milestones": milestones,
        "documents": documents,
        "return_url": reverse("common:coordination_partnerships"),
    }
    return render(request, "coordination/partnership_view.html", context)


@login_required
def partnership_update(request, partnership_id):
    """Update an existing partnership using the shared frontend form."""

    if not request.user.has_perm("coordination.change_partnership"):
        raise PermissionDenied

    partnership = get_object_or_404(
        Partnership.objects.select_related("lead_organization"), pk=partnership_id
    )

    if request.method == "POST":
        form = PartnershipForm(request.POST, request.FILES, instance=partnership)
        signatory_formset = PartnershipSignatoryFormSet(
            request.POST,
            instance=partnership,
            prefix="signatories",
        )
        milestone_formset = PartnershipMilestoneFormSet(
            request.POST,
            instance=partnership,
            prefix="milestones",
        )
        document_formset = PartnershipDocumentFormSet(
            request.POST,
            request.FILES,
            instance=partnership,
            prefix="documents",
        )

        if (
            form.is_valid()
            and signatory_formset.is_valid()
            and milestone_formset.is_valid()
            and document_formset.is_valid()
        ):
            with transaction.atomic():
                partnership = form.save(commit=False)
                partnership.save()
                if hasattr(form, "save_m2m"):
                    form.save_m2m()

                signatory_formset.save()
                milestone_formset.save()
                document_formset.save()

            messages.success(request, "Partnership successfully updated.")
            return redirect("common:coordination_partnership_view", partnership.pk)
    else:
        form = PartnershipForm(instance=partnership)
        signatory_formset = PartnershipSignatoryFormSet(
            instance=partnership,
            prefix="signatories",
        )
        milestone_formset = PartnershipMilestoneFormSet(
            instance=partnership,
            prefix="milestones",
        )
        document_formset = PartnershipDocumentFormSet(
            instance=partnership,
            prefix="documents",
        )

    context = {
        "form": form,
        "signatory_formset": signatory_formset,
        "milestone_formset": milestone_formset,
        "document_formset": document_formset,
        "partnership": partnership,
        "return_url": reverse("common:coordination_partnerships"),
        "page_title": "Edit Partnership",
        "breadcrumb_label": "Edit Partnership",
        "page_heading": f"Edit {partnership.title}",
        "submit_label": "Save changes",
        "is_edit": True,
    }
    return render(request, "coordination/partnership_form.html", context)


@login_required
@require_POST
def partnership_delete(request, partnership_id):
    """Delete an existing partnership entry."""
    if not request.user.has_perm("coordination.delete_partnership"):
        raise PermissionDenied

    partnership = get_object_or_404(Partnership, pk=partnership_id)
    title = partnership.title

    with transaction.atomic():
        partnership.delete()

    messages.success(request, f'Partnership "{title}" has been removed.')
    return redirect("common:coordination_partnerships")


@login_required
def event_create(request):
    """Render and process the frontend coordination event creation form."""

    if not request.user.has_perm("coordination.add_event"):
        raise PermissionDenied

    initial = {
        "organizer": request.user.pk,
        "status": "planned",
        "priority": "medium",
        "start_date": timezone.now().date(),
    }

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            if not event.organizer_id:
                event.organizer = request.user
            event.created_by = request.user
            event.save()
            if hasattr(form, "save_m2m"):
                form.save_m2m()
            messages.success(request, "Event successfully scheduled.")
            return redirect("common:coordination_events")
        messages.error(request, "Please correct the highlighted errors before submitting.")
        if form.errors:
            logger.warning("Event form errors: %s", form.errors)
    else:
        form = EventForm(initial=initial)

    context = {
        "form": form,
        "return_url": reverse("common:coordination_events"),
        "page_title": "Schedule Coordination Event",
        "page_heading": "Schedule New Coordination Event",
        "submit_label": "Create Event",
    }
    return render(request, "coordination/event_form.html", context)


@login_required
def engagement_create(request):
    """Render and process creation of coordination activities."""

    if not request.user.has_perm("coordination.add_stakeholderengagement"):
        raise PermissionDenied

    initial = {
        "status": "planned",
        "priority": "medium",
        "planned_date": timezone.now().replace(
            hour=9, minute=0, second=0, microsecond=0
        ),
    }

    if request.method == "POST":
        form = StakeholderEngagementForm(request.POST)
        if form.is_valid():
            engagement = form.save(commit=False)
            engagement.created_by = request.user
            engagement.save()
            if hasattr(form, "save_m2m"):
                form.save_m2m()
            messages.success(
                request, "Coordination activity recorded successfully."
            )
            return redirect("common:coordination_home")
        messages.error(request, "Please correct the highlighted errors before submitting.")
        if form.errors:
            logger.warning(
                "Stakeholder engagement form errors: %s", form.errors
            )
    else:
        form = StakeholderEngagementForm(initial=initial)

    context = {
        "form": form,
        "return_url": reverse("common:coordination_home"),
        "page_title": "Log Coordination Activity",
        "page_heading": "Record Coordination Activity",
        "submit_label": "Save Activity",
    }
    return render(request, "coordination/activity_form.html", context)


@login_required
def calendar_overview(request):
    """Visualise coordination events and activities on a shared calendar."""

    events = Event.objects.select_related("community", "organizer")
    engagements = StakeholderEngagement.objects.select_related(
        "community",
        "engagement_type",
    )

    def _combine_date_time(date_part, time_part):
        if not date_part:
            return None
        base_time = time_part or time.min
        return datetime.combine(date_part, base_time)

    def _iso(dt_value):
        if not dt_value:
            return None
        if timezone.is_aware(dt_value):
            dt_value = timezone.localtime(dt_value)
        return dt_value.isoformat()

    calendar_entries = []

    for event in events:
        start_dt = _combine_date_time(event.start_date, event.start_time)
        all_day = event.start_time is None

        if event.end_date:
            end_time = event.end_time if event.end_time else (time.max if not all_day else time.max)
            end_dt = _combine_date_time(event.end_date, end_time)
            if all_day and end_dt:
                end_dt = end_dt + timedelta(days=1)
        elif event.end_time:
            end_dt = _combine_date_time(event.start_date, event.end_time)
        elif event.duration_hours and start_dt:
            end_dt = start_dt + timedelta(hours=float(event.duration_hours))
        elif all_day and start_dt:
            end_dt = start_dt + timedelta(days=1)
        else:
            end_dt = start_dt

        calendar_entries.append(
            {
                "id": str(event.pk),
                "title": event.title,
                "start": _iso(start_dt),
                "end": _iso(end_dt),
                "allDay": all_day,
                "backgroundColor": "#2563eb",
                "borderColor": "#1d4ed8",
                "textColor": "#ffffff" if all_day else None,
                "extendedProps": {
                    "type": "event",
                    "status": event.status,
                    "community": getattr(event.community, "name", ""),
                },
            }
        )

    for engagement in engagements:
        start_dt = engagement.planned_date
        end_dt = None
        if engagement.duration_minutes and start_dt:
            end_dt = start_dt + timedelta(minutes=engagement.duration_minutes)

        calendar_entries.append(
            {
                "id": str(engagement.pk),
                "title": engagement.title,
                "start": _iso(start_dt),
                "end": _iso(end_dt),
                "allDay": False,
                "backgroundColor": "#059669",
                "borderColor": "#047857",
                "extendedProps": {
                    "type": "activity",
                    "status": engagement.status,
                    "community": getattr(engagement.community, "name", ""),
                    "engagementType": getattr(
                        engagement.engagement_type, "name", ""
                    ),
                },
            }
        )

    now = timezone.now()
    upcoming_events = events.filter(start_date__gte=now.date()).count()
    past_events = events.filter(start_date__lt=now.date()).count()
    upcoming_engagements = engagements.filter(planned_date__gte=now).count()

    upcoming_event_list = (
        events.filter(start_date__gte=now.date())
        .order_by("start_date", "start_time")[:5]
    )
    upcoming_engagement_list = (
        engagements.filter(planned_date__gte=now)
        .order_by("planned_date")[:5]
    )

    stats = {
        "events": {
            "total": events.count(),
            "upcoming": upcoming_events,
            "past": past_events,
            "completed": events.filter(status="completed").count(),
        },
        "activities": {
            "total": engagements.count(),
            "upcoming": upcoming_engagements,
            "completed": engagements.filter(status="completed").count(),
        },
    }

    context = {
        "calendar_events": calendar_entries,
        "calendar_events_json": json.dumps(calendar_entries),
        "calendar_options_json": json.dumps(
            {
                "initialView": "dayGridMonth",
                "height": "auto",
            }
        ),
        "stats": stats,
        "upcoming_events": upcoming_event_list,
        "upcoming_engagements": upcoming_engagement_list,
    }
    return render(request, "coordination/calendar.html", context)
