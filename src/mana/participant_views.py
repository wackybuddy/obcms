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
    WorkshopNotification,
    WorkshopParticipantAccount,
    WorkshopResponse,
)
from .schema import get_questions_for_workshop
from .services.workshop_access import WorkshopAccessManager


@login_required
@participant_required
def participant_assessments_list(request):
    """List all assessments the participant is registered for."""
    user = request.user

    # Get all assessments where user has WorkshopParticipantAccount
    participant_accounts = WorkshopParticipantAccount.objects.filter(
        user=user
    ).select_related('assessment', 'province')

    assessments_data = []
    for account in participant_accounts:
        assessment = account.assessment

        # Calculate progress
        total_workshops = 5
        completed_workshops = len(account.completed_workshops or [])
        progress_pct = (completed_workshops / total_workshops) * 100

        # Determine status
        if progress_pct == 100:
            status = "completed"
        elif progress_pct > 0:
            status = "active"
        else:
            status = "not_started"

        assessments_data.append({
            'account': account,
            'assessment': assessment,
            'progress_pct': progress_pct,
            'completed_workshops': completed_workshops,
            'total_workshops': total_workshops,
            'status': status,
            'current_workshop_display': account.get_current_workshop_display() if hasattr(account, 'get_current_workshop_display') else account.current_workshop,
        })

    context = {
        'assessments': assessments_data,
    }
    return render(request, 'mana/participant/assessments_list.html', context)


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

    # Get unread notifications
    unread_notifications = WorkshopNotification.objects.filter(
        participant=participant,
        is_read=False
    )[:5]  # Limit to 5 most recent

    # Get recent notifications (last 10)
    recent_notifications = WorkshopNotification.objects.filter(
        participant=participant
    )[:10]

    current_workshop_item = next(
        (item for item in nav_items if item["is_current"]),
        None,
    )
    actionable_workshop_item = next(
        (
            item
            for item in nav_items
            if item["accessible"] and not item["completed"]
        ),
        None,
    )

    # Prefer the next actionable workshop, otherwise fall back to the current one
    quick_action_item = actionable_workshop_item or current_workshop_item

    quick_action = None
    if quick_action_item:
        workshop = quick_action_item["workshop"]
        workshop_number = workshop.get_workshop_type_display().split(":")[0]
        quick_action = {
            "url": quick_action_item["url"],
            "id": workshop.id,
            "title": workshop.title,
            "number": workshop_number,
            "status": workshop.get_status_display(),
            "scheduled_date": workshop.scheduled_date,
            "start_time": workshop.start_time,
            "end_time": workshop.end_time,
        }

    context = {
        "assessment": assessment,
        "participant": participant,
        "nav_items": nav_items,
        "progress": progress,
        "unread_notifications": unread_notifications,
        "recent_notifications": recent_notifications,
        "unread_count": unread_notifications.count(),
        "quick_action": quick_action,
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
            "office_business_name",
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
def participant_workshop_review(request, assessment_id, workshop_type):
    """
    Display submitted workshop responses in read-only format.
    Shows after participant submits workshop - waiting for facilitator to advance.
    """
    assessment = request.mana_assessment
    participant = request.mana_participant_account

    workshop = get_object_or_404(
        WorkshopActivity, assessment=assessment, workshop_type=workshop_type
    )

    # Must have submitted responses
    responses = WorkshopResponse.objects.filter(
        participant=participant,
        workshop=workshop,
        status="submitted"
    ).order_by("question_id")

    if not responses.exists():
        # Not submitted yet, redirect to workshop detail
        return redirect(
            "mana:participant_workshop_detail",
            assessment_id=str(assessment.id),
            workshop_type=workshop_type
        )

    # Get questions for this workshop
    questions = get_questions_for_workshop(workshop_type)

    # Check if facilitator has advanced cohort to next workshop
    access_manager = WorkshopAccessManager(assessment)
    allowed_workshops = access_manager.get_allowed_workshops(participant)

    # Find next workshop in sequence
    try:
        current_index = WorkshopAccessManager.WORKSHOP_SEQUENCE.index(workshop_type)
        if current_index < len(WorkshopAccessManager.WORKSHOP_SEQUENCE) - 1:
            next_workshop_type = WorkshopAccessManager.WORKSHOP_SEQUENCE[current_index + 1]
            next_workshop_unlocked = next_workshop_type in allowed_workshops
            if next_workshop_unlocked:
                next_workshop = WorkshopActivity.objects.filter(
                    assessment=assessment, workshop_type=next_workshop_type
                ).first()
            else:
                next_workshop = None
        else:
            next_workshop_type = None
            next_workshop_unlocked = False
            next_workshop = None
    except ValueError:
        next_workshop_type = None
        next_workshop_unlocked = False
        next_workshop = None

    # Get submission stats
    total_participants = WorkshopParticipantAccount.objects.filter(
        assessment=assessment
    ).count()

    submitted_count = WorkshopResponse.objects.filter(
        workshop=workshop,
        status="submitted"
    ).values("participant").distinct().count()

    # Pair questions with responses
    qa_pairs = []
    for question in questions:
        response = responses.filter(question_id=question["id"]).first()
        qa_pairs.append({
            "question": question,
            "response": response,
        })

    # Get submission timestamp
    first_response = responses.first()
    submitted_at = first_response.submitted_at if first_response else None

    context = {
        "assessment": assessment,
        "participant": participant,
        "workshop": workshop,
        "qa_pairs": qa_pairs,
        "next_workshop_unlocked": next_workshop_unlocked,
        "next_workshop": next_workshop,
        "next_workshop_type": next_workshop_type,
        "submitted_at": submitted_at,
        "total_participants": total_participants,
        "submitted_count": submitted_count,
    }
    return render(request, "mana/participant/workshop_review.html", context)


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

    # Check if workshop has already been submitted (read-only mode)
    is_submitted = responses.filter(status="submitted").exists()

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

    if request.method == "POST":
        # Block editing if workshop is already submitted
        if is_submitted:
            messages.error(
                request,
                f"This workshop has already been submitted and cannot be edited. "
                f"Your responses are locked to maintain data integrity."
            )
            return redirect(
                "mana:participant_workshop_detail",
                assessment_id=str(assessment.id),
                workshop_type=workshop_type
            )

        if form.is_valid():
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
                    # Redirect to outputs page to review submission
                    next_url = reverse(
                        "mana:participant_workshop_outputs",
                        args=[str(assessment.id), workshop_type],
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
                # Redirect to outputs page to review submission
                return redirect(
                    "mana:participant_workshop_outputs",
                    assessment_id=str(assessment.id),
                    workshop_type=workshop_type,
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
        "is_submitted": is_submitted,
    }
    return render(request, "mana/participant/workshop_detail.html", context)


@login_required
@participant_required
def participant_workshop_outputs(request, assessment_id, workshop_type):
    """Show participant their submitted workshop responses with advancement status."""
    assessment = request.mana_assessment
    participant = request.mana_participant_account

    # Get workshop
    workshop = get_object_or_404(
        WorkshopActivity,
        assessment=assessment,
        workshop_type=workshop_type
    )

    # Verify this workshop has been submitted
    if workshop_type not in (participant.completed_workshops or []):
        messages.error(request, "You haven't submitted this workshop yet.")
        return redirect('mana:participant_workshop_detail', assessment_id, workshop_type)

    # Get all responses for this workshop
    responses = WorkshopResponse.objects.filter(
        participant=participant,
        workshop=workshop,
        status="submitted"
    ).order_by('question_id')

    # Get questions from schema
    questions = get_questions_for_workshop(workshop_type)

    # Pair questions with responses
    qa_pairs = []
    for question in questions:
        response = responses.filter(question_id=question['id']).first()
        qa_pairs.append({
            'question': question,
            'response': response,
        })

    # Check advancement status
    # Participant is advanced if current_workshop has moved past this workshop
    workshop_sequence = WorkshopAccessManager.WORKSHOP_SEQUENCE
    try:
        current_index = workshop_sequence.index(workshop_type)
        current_workshop_index = workshop_sequence.index(participant.current_workshop) if participant.current_workshop in workshop_sequence else 0
        is_advanced = current_workshop_index > current_index
    except ValueError:
        is_advanced = False

    # Get next workshop info if advanced
    next_workshop = None
    if is_advanced:
        if current_index + 1 < len(workshop_sequence):
            next_workshop_type = workshop_sequence[current_index + 1]
            next_workshop = WorkshopActivity.objects.filter(
                assessment=assessment,
                workshop_type=next_workshop_type
            ).first()

    # Get submission progress
    total_participants = WorkshopParticipantAccount.objects.filter(
        assessment=assessment
    ).count()

    submitted_participants = WorkshopResponse.objects.filter(
        workshop=workshop,
        status="submitted"
    ).values('participant').distinct().count()

    # Get submission timestamp
    submission_timestamp = responses.first().updated_at if responses.exists() else None

    context = {
        'assessment': assessment,
        'participant': participant,
        'workshop': workshop,
        'qa_pairs': qa_pairs,
        'is_advanced': is_advanced,
        'next_workshop': next_workshop,
        'total_participants': total_participants,
        'submitted_participants': submitted_participants,
        'submission_timestamp': submission_timestamp,
    }
    return render(request, 'mana/participant/workshop_outputs.html', context)


@login_required
@participant_required
@require_http_methods(["POST"])
def mark_notification_read(request, assessment_id, notification_id):
    """Mark a notification as read."""
    participant = request.mana_participant_account

    notification = get_object_or_404(
        WorkshopNotification,
        id=notification_id,
        participant=participant
    )

    notification.mark_as_read()

    if request.headers.get("HX-Request"):
        return HttpResponse(status=204)

    return redirect("mana:participant_dashboard", assessment_id=str(assessment_id))
