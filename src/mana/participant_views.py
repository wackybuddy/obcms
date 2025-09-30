"""Participant-facing views for Regional MANA workshops."""

from __future__ import annotations

import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseForbidden,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .decorators import participant_required
from .forms import ParticipantOnboardingForm, ParticipantProfileForm, WorkshopResponseForm
from .models import (
    Assessment,
    WorkshopAccessLog,
    WorkshopActivity,
    WorkshopParticipantAccount,
    WorkshopResponse,
)
from .schema import get_questions_for_workshop
from .services.workshop_access import WorkshopAccessManager


def _build_workshop_navigation(assessment: Assessment, participant: WorkshopParticipantAccount):
    """Return navigation metadata for the participant dashboard."""
    access_manager = WorkshopAccessManager(assessment)
    allowed = set(access_manager.get_allowed_workshops(participant))
    completed = set(participant.completed_workshops or [])

    allowed_sequence = WorkshopAccessManager.WORKSHOP_SEQUENCE
    activities = {
        workshop.workshop_type: workshop
        for workshop in WorkshopActivity.objects.filter(
            assessment=assessment,
            workshop_type__in=allowed_sequence,
        )
    }

    nav_items = []
    for workshop_type in allowed_sequence:
        workshop = activities.get(workshop_type)
        if not workshop:
            continue
        nav_items.append(
            {
                "workshop": workshop,
                "accessible": workshop.workshop_type in allowed,
                "completed": workshop.workshop_type in completed,
                "is_current": workshop.workshop_type
                == (participant.current_workshop or "workshop_1"),
                "url": reverse(
                    "mana:participant_workshop_detail",
                    args=[str(assessment.id), workshop.workshop_type],
                ),
            }
        )

    progress = access_manager.get_progress_summary(participant)
    return nav_items, progress


def _log_workshop_action(participant, workshop, action_type, metadata=None):
    """Persist a workshop access log entry."""
    WorkshopAccessLog.objects.create(
        participant=participant,
        workshop=workshop,
        action_type=action_type,
        metadata=metadata or {},
    )


@login_required
@participant_required
def participant_dashboard(request, assessment_id):
    assessment = request.mana_assessment
    participant = request.mana_participant_account

    if not participant.consent_given or not participant.profile_completed:
        return redirect(
            "mana:participant_onboarding", assessment_id=str(assessment.id)
        )

    nav_items, progress = _build_workshop_navigation(assessment, participant)

    context = {
        "assessment": assessment,
        "participant": participant,
        "nav_items": nav_items,
        "progress": progress,
    }

    if request.headers.get("HX-Request"):
        return render(
            request,
            "mana/participant/partials/workshop_nav.html",
            context,
        )

    return render(request, "mana/participant/dashboard.html", context)


@login_required
@participant_required
@require_http_methods(["GET", "POST"])
def participant_onboarding(request, assessment_id):
    assessment = request.mana_assessment
    participant = request.mana_participant_account

    if participant.consent_given and participant.profile_completed:
        return redirect(
            "mana:participant_dashboard", assessment_id=str(assessment.id)
        )

    form = ParticipantOnboardingForm(
        data=request.POST or None,
        instance=participant,
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        password = form.cleaned_data.get("password")
        if password:
            request.user.set_password(password)
            request.user.save(update_fields=["password"])
            update_session_auth_hash(request, request.user)

        gave_consent = form.cleaned_data.get("consent", False)
        participant.profile_completed = True
        if gave_consent and not participant.consent_given:
            participant.consent_given = True
            participant.consent_date = timezone.now()
        participant.current_workshop = participant.current_workshop or "workshop_1"
        participant.save(update_fields=[
            "stakeholder_type",
            "organization",
            "province",
            "municipality",
            "barangay",
            "profile_completed",
            "consent_given",
            "consent_date",
            "current_workshop",
            "updated_at",
        ])

        messages.success(request, "Profile updated. You're ready for Workshop 1.")

        redirect_url = reverse(
            "mana:participant_dashboard", args=[str(assessment.id)]
        )
        if request.headers.get("HX-Request"):
            response = HttpResponse(status=204)
            response["HX-Redirect"] = redirect_url
            response["HX-Trigger"] = json.dumps(
                {
                    "show-toast": {
                        "message": "Profile saved. Workshop 1 unlocked.",
                        "level": "success",
                    }
                }
            )
            return response
        return redirect(redirect_url)

    context = {
        "assessment": assessment,
        "participant": participant,
        "form": form,
    }
    return render(request, "mana/participant/onboarding.html", context)


@login_required
@participant_required
@require_http_methods(["GET", "POST"])
def participant_workshop_detail(request, assessment_id, workshop_type):
    assessment = request.mana_assessment
    participant = request.mana_participant_account

    workshop = get_object_or_404(
        WorkshopActivity, assessment=assessment, workshop_type=workshop_type
    )

    access_manager = WorkshopAccessManager(assessment)
    if not access_manager.is_workshop_accessible(participant, workshop_type):
        return HttpResponseForbidden("Workshop locked. Await facilitator approval.")

    questions = get_questions_for_workshop(workshop_type)
    responses = (
        WorkshopResponse.objects.filter(participant=participant, workshop=workshop)
        .order_by("question_id")
    )

    existing_responses = {}
    for response in responses:
        data = response.response_data
        if isinstance(data, (dict, list)):
            existing_responses[response.question_id] = json.dumps(data)
        else:
            existing_responses[response.question_id] = data

    form = WorkshopResponseForm(
        data=request.POST or None,
        questions_schema=questions,
        existing_responses=existing_responses,
    )

    if request.method == "GET":
        _log_workshop_action(
            participant,
            workshop,
            "view",
            metadata={"at": timezone.now().isoformat()},
        )

    if request.method == "POST" and form.is_valid():
        action = request.POST.get("action")
        if not action and request.headers.get("HX-Request"):
            action = "autosave"
        elif not action:
            action = "save_draft"

        saved_status = "draft"
        if action == "submit":
            saved_status = "submitted"

        with transaction.atomic():
            for question in questions:
                question_id = question["id"]
                value = form.cleaned_data.get(question_id)

                if question.get("type") in {"repeater", "structured"}:
                    if value:
                        try:
                            parsed_value = json.loads(value)
                        except json.JSONDecodeError:
                            parsed_value = []
                        data_value = parsed_value
                    else:
                        data_value = []
                else:
                    data_value = value

                response, _ = WorkshopResponse.objects.get_or_create(
                    participant=participant,
                    workshop=workshop,
                    question_id=question_id,
                    defaults={
                        "response_data": data_value,
                        "status": saved_status,
                    },
                )

                response.response_data = data_value
                response.status = saved_status
                if saved_status == "submitted":
                    response.submitted_at = response.submitted_at or timezone.now()
                response.save()

        if saved_status == "submitted":
            access_manager.mark_workshop_complete(
                participant,
                workshop_type,
                metadata={"submitted_at": timezone.now().isoformat()},
            )
            participant.refresh_from_db(fields=["current_workshop", "completed_workshops"])
            _log_workshop_action(
                participant,
                workshop,
                "submit",
                metadata={"submitted_at": timezone.now().isoformat()},
            )
            messages.success(
                request, "Workshop submitted. We'll move you to the next session."
            )
        else:
            _log_workshop_action(
                participant,
                workshop,
                "update",
                metadata={"saved_at": timezone.now().isoformat(), "status": saved_status},
            )
            messages.info(request, "Draft saved. You can continue anytime.")

        nav_items, progress = _build_workshop_navigation(assessment, participant)

        if request.headers.get("HX-Request"):
            if saved_status == "submitted":
                next_url = (
                    reverse(
                        "mana:participant_workshop_detail",
                        args=[str(assessment.id), participant.current_workshop],
                    )
                    if participant.current_workshop
                    else reverse(
                        "mana:participant_dashboard", args=[str(assessment.id)]
                    )
                )
                response = HttpResponse(status=204)
                response["HX-Redirect"] = next_url
                response["HX-Trigger"] = json.dumps(
                    {
                        "refresh-workshop-nav": {
                            "assessment": str(assessment.id),
                            "current": participant.current_workshop,
                        },
                        "show-toast": {
                            "message": "Workshop submitted successfully.",
                            "level": "success",
                        },
                    }
                )
                return response

            context = {
                "saved_at": timezone.now(),
                "status": saved_status,
            }
            response = render(
                request,
                "mana/participant/partials/autosave_status.html",
                context,
            )
            response["HX-Trigger"] = json.dumps(
                {
                    "refresh-workshop-nav": {
                        "assessment": str(assessment.id),
                        "current": participant.current_workshop,
                        "progress": progress,
                    },
                    "show-toast": {
                        "message": "Draft saved",
                        "level": "info",
                    },
                }
            )
            return response

        if saved_status == "submitted":
            if participant.current_workshop:
                return redirect(
                    "mana:participant_workshop_detail",
                    assessment_id=str(assessment.id),
                    workshop_type=participant.current_workshop,
                )
            return redirect(
                "mana:participant_dashboard", assessment_id=str(assessment.id)
            )

        return redirect(
            "mana:participant_workshop_detail",
            assessment_id=str(assessment.id),
            workshop_type=workshop_type,
        )

    nav_items, progress = _build_workshop_navigation(assessment, participant)

    question_field_pairs = []
    for question in questions:
        question_id = question.get("id")
        if not question_id:
            continue
        if question_id not in form.fields:
            continue
        question_field_pairs.append(
            {
                "question": question,
                "field": form[question_id],
            }
        )

    context = {
        "assessment": assessment,
        "participant": participant,
        "workshop": workshop,
        "form": form,
        "questions": questions,
        "question_field_pairs": question_field_pairs,
        "nav_items": nav_items,
        "progress": progress,
    }
    return render(request, "mana/participant/workshop_detail.html", context)
