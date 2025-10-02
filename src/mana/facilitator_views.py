"""Facilitator-facing views for Regional MANA workshops."""

from __future__ import annotations

import csv
import io
import json
from collections import defaultdict
from typing import Dict, List, Tuple

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.views.decorators.http import require_http_methods

try:
    from openpyxl import Workbook
except ImportError:  # pragma: no cover - handled gracefully at runtime
    Workbook = None

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:  # pragma: no cover
    canvas = None
    letter = None

from common.models import Province

from .decorators import facilitator_required
from .forms import (
    FacilitatorBulkImportForm,
    FacilitatorParticipantForm,
    WorkshopSynthesisRequestForm,
)
from .models import (
    Assessment,
    FacilitatorAssessmentAssignment,
    WorkshopActivity,
    WorkshopNotification,
    WorkshopParticipantAccount,
    WorkshopResponse,
    WorkshopSynthesis,
)
from .schema import get_questions_for_workshop
from .services.workshop_access import WorkshopAccessManager
from .services.workshop_synthesis import AIWorkshopSynthesizer
from .tasks import generate_workshop_synthesis as task_generate_workshop_synthesis

User = get_user_model()


def _build_navigation(assessment: Assessment) -> List[Dict]:
    workshops = WorkshopActivity.objects.filter(assessment=assessment).order_by(
        "workshop_day", "start_time"
    )
    return list(workshops)


def _get_filtered_responses(
    workshop: WorkshopActivity,
    province_id: str = None,
    stakeholder_type: str = None,
) -> List[WorkshopResponse]:
    responses = WorkshopResponse.objects.filter(workshop=workshop).select_related(
        "participant__user",
        "participant__province",
        "participant__municipality",
    )

    if province_id:
        responses = responses.filter(participant__province_id=province_id)

    if stakeholder_type:
        responses = responses.filter(participant__stakeholder_type=stakeholder_type)

    return list(responses)


def _group_responses_by_question(
    responses: List[WorkshopResponse], questions: List[dict]
) -> List[Dict]:
    question_map = {q["id"]: q for q in questions}
    grouped: Dict[str, Dict] = defaultdict(lambda: {"question": None, "responses": []})

    for question in questions:
        grouped[question["id"]]["question"] = question

    for response in responses:
        entry = grouped[response.question_id]
        participant = response.participant
        entry["responses"].append(
            {
                "participant": participant,
                "organization": participant.office_business_name,
                "province": participant.province,
                "stakeholder": participant.get_stakeholder_type_display(),
                "status": response.status,
                "submitted_at": response.submitted_at,
                "data": response.response_data,
                "rendered": (
                    json.dumps(
                        response.response_data,
                        ensure_ascii=False,
                        indent=2,
                    )
                    if isinstance(response.response_data, (dict, list))
                    else response.response_data
                ),
                "is_structured": isinstance(response.response_data, (dict, list)),
            }
        )

    return [grouped[q["id"]] for q in questions]


def _ensure_participant_permissions(user: User):
    group, _ = Group.objects.get_or_create(name="mana_regional_participant")
    user.groups.add(group)

    for codename in ["can_access_regional_mana", "can_view_provincial_obc"]:
        try:
            permission = Permission.objects.get(codename=codename)
            user.user_permissions.add(permission)
        except Permission.DoesNotExist:  # pragma: no cover - safeguard
            continue


def _build_participant_table(participants, assessment) -> dict:
    headers = [
        {"label": "Participant"},
        {"label": "Stakeholder"},
        {"label": "Province"},
        {"label": "Progress"},
    ]

    rows = []
    total_workshops = len(WorkshopAccessManager.WORKSHOP_SEQUENCE)

    for participant in participants:
        name = participant.user.get_full_name() or participant.user.email
        stakeholder = participant.get_stakeholder_type_display()
        province = participant.province.name if participant.province else "—"
        completed = len(participant.completed_workshops or [])
        percentage = int((completed / total_workshops) * 100)
        reset_url = reverse(
            "mana:facilitator_reset_participant",
            args=[assessment.id, participant.id],
        )
        progress_html = (
            "<div class='space-y-2'>"
            f"<div class='flex items-center justify-between text-xs text-gray-500'><span>{completed}/{total_workshops} workshops</span><span>{percentage}%</span></div>"
            f"<div class='w-full bg-gray-100 rounded-full h-2'><div class='bg-emerald-500 h-2 rounded-full' style='width: {percentage}%;'></div></div>"
            f"<button type='button' class='inline-flex items-center gap-1 rounded-lg border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700 hover:bg-amber-100' hx-post='{reset_url}' hx-target='#participants-card' hx-swap='outerHTML swap:300ms'><i class='fas fa-undo'></i>Reset</button>"
            "</div>"
        )

        rows.append(
            {
                "cells": [
                    {
                        "content": (
                            f"<div class='font-semibold text-gray-900'>{name}</div>"
                            f"<div class='text-xs text-gray-400'>{participant.user.email}</div>"
                        )
                    },
                    {"content": stakeholder},
                    {"content": province},
                    {"content": progress_html},
                ],
                "view_url": reverse(
                    "admin:mana_workshopparticipantaccount_change",
                    args=[participant.id],
                ),
                "edit_url": reverse(
                    "admin:mana_workshopparticipantaccount_change",
                    args=[participant.id],
                ),
                "delete_preview_url": reverse(
                    "admin:mana_workshopparticipantaccount_delete",
                    args=[participant.id],
                ),
            }
        )

    return {"headers": headers, "rows": rows}


def _build_question_table(grouped_responses: List[Dict]) -> dict:
    headers = [
        {"label": "Question"},
        {"label": "Responses"},
        {"label": "Last Submitted"},
    ]

    rows = []
    for entry in grouped_responses:
        question = entry.get("question", {})
        responses = entry.get("responses", [])
        question_id = question.get("id", "")

        latest = None
        timestamps = [
            resp.get("submitted_at") for resp in responses if resp.get("submitted_at")
        ]
        if timestamps:
            latest_dt = max(timestamps)
            if latest_dt:
                latest = timezone.localtime(latest_dt).strftime("%b %d, %Y %H:%M")

        question_html = (
            f"<div class='font-semibold text-gray-900'>{question.get('text', 'Untitled Question')}</div>"
            f"<div class='text-xs text-gray-400'>{question.get('category', 'General')}</div>"
        )

        rows.append(
            {
                "cells": [
                    {"content": question_html},
                    {"content": str(len(responses))},
                    {"content": latest or "—"},
                ],
                "view_url": f"#question-{question_id}",
                "edit_url": f"#question-{question_id}",
                "delete_preview_url": "#",
            }
        )

    return {"headers": headers, "rows": rows}


@login_required
@facilitator_required
def manage_participants(request, assessment_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    participants = (
        WorkshopParticipantAccount.objects.filter(assessment=assessment)
        .select_related("user", "province", "municipality")
        .order_by("user__last_name")
    )

    registration_form = FacilitatorParticipantForm()
    bulk_form = FacilitatorBulkImportForm()

    if request.method == "POST":
        form_type = request.POST.get("form_type", "single")

        if form_type == "single":
            registration_form = FacilitatorParticipantForm(request.POST)
            if registration_form.is_valid():
                data = registration_form.cleaned_data
                email = data.get("email")
                first_name = data.get("first_name", "Participant")
                last_name = data.get("last_name", "")

                if User.objects.filter(username=email).exists():
                    messages.error(request, "A user with that email already exists.")
                else:
                    with transaction.atomic():
                        temp_password = (
                            data.get("temp_password")
                            or User.objects.make_random_password()
                        )
                        user = User.objects.create_user(
                            username=email,
                            email=email,
                            first_name=first_name,
                            last_name=last_name,
                            password=temp_password,
                        )
                        _ensure_participant_permissions(user)

                        participant = registration_form.save(commit=False)
                        participant.assessment = assessment
                        participant.user = user
                        participant.created_by = request.user
                        participant.current_workshop = "workshop_1"
                        participant.completed_workshops = []
                        participant.consent_given = False
                        participant.consent_date = None
                        participant.profile_completed = False
                        participant.save()

                    messages.success(
                        request,
                        f"Participant {user.get_full_name() or user.email} added successfully.",
                    )
                    if not data.get("temp_password"):
                        messages.info(
                            request,
                            f"Generated temporary password for {user.email}: {temp_password}",
                        )
                    return redirect(
                        "mana:facilitator_manage_participants",
                        assessment_id=str(assessment.id),
                    )

        else:  # bulk import
            bulk_form = FacilitatorBulkImportForm(request.POST, request.FILES)
            if bulk_form.is_valid():
                csv_file = request.FILES["csv_file"]
                decoded = csv_file.read().decode("utf-8")
                reader = csv.DictReader(io.StringIO(decoded))
                created = 0
                for row in reader:
                    email = row.get("email")
                    if not email or User.objects.filter(username=email).exists():
                        continue

                    with transaction.atomic():
                        user = User.objects.create_user(
                            username=email,
                            email=email,
                            first_name=row.get("first_name", ""),
                            last_name=row.get("last_name", ""),
                            password=row.get(
                                "password", User.objects.make_random_password()
                            ),
                        )
                        _ensure_participant_permissions(user)

                        province_id = row.get("province_id") or None
                        region_id = row.get("region_id") or None
                        if not region_id and province_id:
                            region_id = (
                                Province.objects.filter(pk=province_id)
                                .values_list("region_id", flat=True)
                                .first()
                            )

                        participant = WorkshopParticipantAccount.objects.create(
                            assessment=assessment,
                            user=user,
                            stakeholder_type=row.get("stakeholder_type", "other"),
                            region_id=region_id,
                            province_id=province_id,
                            municipality_id=row.get("municipality_id") or None,
                            barangay_id=row.get("barangay_id") or None,
                            office_business_name=(
                                row.get("office_business_name")
                                or row.get("organization", "")
                            ),
                            created_by=request.user,
                            current_workshop="workshop_1",
                            completed_workshops=[],
                            consent_given=False,
                            profile_completed=False,
                        )
                        created += 1

                messages.success(
                    request,
                    f"Imported {created} participants from CSV.",
                )
                return redirect(
                    "mana:facilitator_manage_participants",
                    assessment_id=str(assessment.id),
                )

    participant_table = _build_participant_table(participants, assessment)

    context = {
        "assessment": assessment,
        "participants": participants,
        "registration_form": registration_form,
        "bulk_form": bulk_form,
        "participant_table": participant_table,
    }

    template = (
        "mana/facilitator/partials/participants_card.html"
        if request.headers.get("HX-Request")
        else "mana/facilitator/participants.html"
    )
    return render(request, template, context)


@login_required
@facilitator_required
def facilitator_dashboard(request, assessment_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id)

    workshop_type = request.GET.get("workshop", "workshop_1")
    province_id = request.GET.get("province") or None
    stakeholder_type = request.GET.get("stakeholder") or None

    access_manager = WorkshopAccessManager(assessment)
    auto_unlocked = access_manager.auto_unlock_due_workshops()

    workshops = _build_navigation(assessment)
    workshop = next((w for w in workshops if w.workshop_type == workshop_type), None)
    if not workshop:
        raise Http404("Workshop not found")

    questions = get_questions_for_workshop(workshop_type)
    responses = _get_filtered_responses(workshop, province_id, stakeholder_type)
    grouped_responses = _group_responses_by_question(responses, questions)

    participants = WorkshopParticipantAccount.objects.filter(
        assessment=assessment
    ).select_related("province")
    submitted_count = (
        WorkshopResponse.objects.filter(workshop=workshop, status="submitted")
        .values("participant")
        .distinct()
        .count()
    )

    syntheses = WorkshopSynthesis.objects.filter(workshop=workshop).order_by(
        "-created_at"
    )

    synthesis_form = WorkshopSynthesisRequestForm(assessment=assessment)

    participant_table = _build_participant_table(participants, assessment)
    question_table = _build_question_table(grouped_responses)

    workshop_types = [w.workshop_type for w in workshops]
    current_index = workshop_types.index(workshop.workshop_type)
    next_workshop_type = (
        workshop_types[current_index + 1]
        if current_index < len(workshop_types) - 1
        else None
    )
    next_workshop = None
    if next_workshop_type:
        next_workshop = next(
            (w for w in workshops if w.workshop_type == next_workshop_type),
            None,
        )

    context = {
        "assessment": assessment,
        "workshops": workshops,
        "workshop": workshop,
        "grouped_responses": grouped_responses,
        "participants": participants,
        "total_participants": participants.count(),
        "submitted_count": submitted_count,
        "filters": {
            "province": province_id,
            "stakeholder": stakeholder_type,
        },
        "syntheses": syntheses,
        "synthesis_form": synthesis_form,
        "provinces": sorted(
            {p.province for p in participants if p.province},
            key=lambda province: province.name,
        ),
        "stakeholder_types": WorkshopParticipantAccount.STAKEHOLDER_TYPES,
        "next_workshop_type": next_workshop_type,
        "next_workshop": next_workshop,
        "participant_table": participant_table,
        "question_table": question_table,
        "auto_unlocked": auto_unlocked,
    }

    if request.headers.get("HX-Request"):
        return render(
            request,
            "mana/facilitator/partials/responses_table.html",
            context,
        )

    return render(request, "mana/facilitator/dashboard.html", context)


@login_required
@facilitator_required
@require_http_methods(["POST"])
def advance_workshop(request, assessment_id, workshop_type):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    access_manager = WorkshopAccessManager(assessment)

    moved = access_manager.advance_all_participants(workshop_type, request.user)
    workshop_obj = WorkshopActivity.objects.filter(
        assessment=assessment, workshop_type=workshop_type
    ).first()
    workshop_name = (
        workshop_obj.get_workshop_type_display() if workshop_obj else workshop_type
    )

    # Create notifications for all participants in this assessment
    participants = WorkshopParticipantAccount.objects.filter(assessment=assessment)
    for participant in participants:
        WorkshopNotification.objects.create(
            participant=participant,
            notification_type="workshop_advanced",
            title=f"🎉 New Workshop Available: {workshop_name}",
            message=f"The facilitator has unlocked {workshop_name}. You can now proceed to complete this workshop.",
            workshop=workshop_obj,
        )

    messages.success(request, f"Advanced {moved} participants to {workshop_name}.")

    if request.headers.get("HX-Request"):
        response = HttpResponse(status=204)
        response["HX-Trigger"] = json.dumps(
            {
                "refresh-workshop-nav": {
                    "assessment": str(assessment.id),
                    "current": workshop_type,
                },
                "show-toast": {
                    "message": f"Advanced {moved} participants to {workshop_name}.",
                    "level": "success",
                },
            }
        )
        return response

    return redirect("mana:facilitator_dashboard", assessment_id=str(assessment.id))


@login_required
@facilitator_required
@require_http_methods(["POST"])
def reset_participant_progress(request, assessment_id, participant_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    participant = get_object_or_404(
        WorkshopParticipantAccount,
        pk=participant_id,
        assessment=assessment,
    )

    access_manager = WorkshopAccessManager(assessment)
    access_manager.reset_participant_progress(participant, request.user)

    participants = (
        WorkshopParticipantAccount.objects.filter(assessment=assessment)
        .select_related("user", "province", "municipality")
        .order_by("user__last_name")
    )
    participant_table = _build_participant_table(participants, assessment)

    messages.info(
        request,
        f"Reset progress for {participant.user.get_full_name() or participant.user.email}.",
    )

    context = {
        "assessment": assessment,
        "participants": participants,
        "participant_table": participant_table,
        "registration_form": FacilitatorParticipantForm(),
        "bulk_form": FacilitatorBulkImportForm(),
    }

    if request.headers.get("HX-Request"):
        response = render(
            request,
            "mana/facilitator/partials/participants_card.html",
            context,
        )
        response["HX-Trigger"] = json.dumps(
            {
                "show-toast": {
                    "message": "Participant progress reset.",
                    "level": "info",
                }
            }
        )
        return response

    return redirect(
        "mana:facilitator_manage_participants",
        assessment_id=str(assessment.id),
    )


@login_required
@facilitator_required
@require_http_methods(["POST"])
def generate_synthesis(request, assessment_id, workshop_type):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    workshop = get_object_or_404(
        WorkshopActivity, assessment=assessment, workshop_type=workshop_type
    )

    form = WorkshopSynthesisRequestForm(request.POST, assessment=assessment)
    if not form.is_valid():
        messages.error(request, "Please fix the errors in the synthesis form.")
        return redirect(
            "mana:facilitator_dashboard",
            assessment_id=str(assessment.id),
        )

    filters = {}
    if form.cleaned_data.get("filter_province"):
        filters["province_id"] = form.cleaned_data["filter_province"].id
    if form.cleaned_data.get("filter_stakeholder_type"):
        filters["stakeholder_type"] = form.cleaned_data["filter_stakeholder_type"]

    provider = form.cleaned_data["provider"]
    custom_prompt = form.cleaned_data.get("custom_prompt") or None

    async_enabled = getattr(settings, "MANA_ASYNC_ENABLED", False)

    if async_enabled and hasattr(task_generate_workshop_synthesis, "delay"):
        task_generate_workshop_synthesis.delay(
            workshop.id,
            filters,
            request.user.id,
            provider,
            custom_prompt,
        )
        messages.success(request, "Synthesis queued for background processing.")
    else:
        synthesizer = AIWorkshopSynthesizer(workshop, filters)
        synthesis = synthesizer.synthesize(
            created_by=request.user,
            provider=provider,
            custom_prompt=custom_prompt,
        )

        if synthesis.status == "failed":
            messages.error(request, synthesis.error_message or "Synthesis failed.")
        else:
            messages.success(request, "AI synthesis generated successfully.")

    if request.headers.get("HX-Request"):
        response = HttpResponse(status=204)
        response["HX-Trigger"] = json.dumps(
            {
                "refresh-workshop-nav": {
                    "assessment": str(assessment.id),
                    "current": workshop_type,
                },
                "show-toast": {
                    "message": (
                        "Synthesis queued" if async_enabled else "Synthesis complete"
                    ),
                    "level": "success",
                },
            }
        )
        return response

    return redirect(
        "mana:facilitator_dashboard",
        assessment_id=str(assessment.id),
    )


@login_required
@facilitator_required
@require_http_methods(["POST"])
def regenerate_synthesis(request, assessment_id, synthesis_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    synthesis = get_object_or_404(WorkshopSynthesis, pk=synthesis_id)

    synthesizer = AIWorkshopSynthesizer(synthesis.workshop, synthesis.filters)
    synthesizer.regenerate_synthesis(synthesis, created_by=request.user)
    messages.info(request, "Synthesis regeneration queued.")

    return redirect(
        "mana:facilitator_dashboard",
        assessment_id=str(assessment.id),
    )


@login_required
@facilitator_required
@require_http_methods(["POST"])
def approve_synthesis(request, assessment_id, synthesis_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    synthesis = get_object_or_404(WorkshopSynthesis, pk=synthesis_id)

    synthesizer = AIWorkshopSynthesizer(synthesis.workshop, synthesis.filters)
    synthesizer.approve_synthesis(synthesis, reviewed_by=request.user)
    messages.success(request, "Synthesis approved.")

    return redirect(
        "mana:facilitator_dashboard",
        assessment_id=str(assessment.id),
    )


def _export_as_csv(responses: List[WorkshopResponse]) -> HttpResponse:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Participant",
            "Organization",
            "Province",
            "Stakeholder",
            "Status",
            "Submitted",
            "Question",
            "Response",
        ]
    )

    for response in responses:
        participant = response.participant
        writer.writerow(
            [
                participant.user.get_full_name() or participant.user.email,
                participant.office_business_name,
                participant.province.name if participant.province else "",
                participant.get_stakeholder_type_display(),
                response.status,
                response.submitted_at.isoformat() if response.submitted_at else "",
                response.question_id,
                json.dumps(response.response_data, ensure_ascii=False),
            ]
        )

    result = HttpResponse(output.getvalue(), content_type="text/csv")
    result["Content-Disposition"] = "attachment; filename=workshop_responses.csv"
    return result


def _export_as_xlsx(responses: List[WorkshopResponse]) -> HttpResponse:
    if Workbook is None:
        raise RuntimeError("openpyxl is not installed")

    wb = Workbook()
    ws = wb.active
    ws.title = "Responses"
    ws.append(
        [
            "Participant",
            "Organization",
            "Province",
            "Stakeholder",
            "Status",
            "Submitted",
            "Question",
            "Response",
        ]
    )

    for response in responses:
        participant = response.participant
        ws.append(
            [
                participant.user.get_full_name() or participant.user.email,
                participant.office_business_name,
                participant.province.name if participant.province else "",
                participant.get_stakeholder_type_display(),
                response.status,
                response.submitted_at.isoformat() if response.submitted_at else "",
                response.question_id,
                json.dumps(response.response_data, ensure_ascii=False),
            ]
        )

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=workshop_responses.xlsx"
    return response


def _export_as_pdf(responses: List[WorkshopResponse]) -> HttpResponse:
    if canvas is None or letter is None:
        raise RuntimeError("reportlab is not installed")

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y, "Workshop Responses")
    y -= 30

    pdf.setFont("Helvetica", 10)
    for response in responses:
        participant = response.participant
        text = (
            f"Participant: {participant.user.get_full_name() or participant.user.email}\n"
            f"Organization: {participant.office_business_name}\n"
            f"Province: {participant.province.name if participant.province else ''}\n"
            f"Stakeholder: {participant.get_stakeholder_type_display()}\n"
            f"Question: {response.question_id}\n"
            f"Response: {json.dumps(response.response_data, ensure_ascii=False)}\n"
        )
        for line in text.split("\n"):
            pdf.drawString(40, y, line[:95])
            y -= 14
            if y < 60:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 10)
        y -= 10

    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=workshop_responses.pdf"
    return response


@login_required
@facilitator_required
def export_workshop_responses(request, assessment_id, workshop_type, format_type):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    workshop = get_object_or_404(
        WorkshopActivity, assessment=assessment, workshop_type=workshop_type
    )

    province_id = request.GET.get("province")
    stakeholder_type = request.GET.get("stakeholder")

    responses = _get_filtered_responses(workshop, province_id, stakeholder_type)

    try:
        if format_type == "csv":
            return _export_as_csv(responses)
        if format_type == "xlsx":
            return _export_as_xlsx(responses)
        if format_type == "pdf":
            return _export_as_pdf(responses)
    except RuntimeError as exc:
        messages.error(request, str(exc))
        return redirect(
            "mana:facilitator_dashboard",
            assessment_id=str(assessment.id),
        )

    return HttpResponseBadRequest("Unsupported export format")


@login_required
def create_account(request):
    """Create MANA Facilitator or Participant accounts."""
    # Import here to avoid circular imports
    from common.models import Province
    from .forms import AccountCreationForm

    # Check if user is staff or superuser
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "You don't have permission to create accounts.")
        return redirect("common:dashboard")

    if request.method == "POST":
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            try:
                account_type = form.cleaned_data["account_type"]
                username = form.cleaned_data["username"]
                email = form.cleaned_data["email"]
                first_name = form.cleaned_data["first_name"]
                last_name = form.cleaned_data["last_name"]
                password = form.cleaned_data["password"]

                # Create User
                User = get_user_model()
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                )

                if account_type == "facilitator":
                    # Grant facilitator permissions
                    # Facilitators need all three permissions to:
                    # 1. Facilitate workshops (can_facilitate_workshop)
                    # 2. View regional MANA content that participants see (can_access_regional_mana)
                    # 3. View provincial OBC data for context (can_view_provincial_obc)
                    facilitator_permissions = [
                        "can_facilitate_workshop",
                        "can_access_regional_mana",
                        "can_view_provincial_obc",
                    ]
                    for perm_codename in facilitator_permissions:
                        try:
                            permission = Permission.objects.get(codename=perm_codename)
                            user.user_permissions.add(permission)
                        except Permission.DoesNotExist:
                            pass  # Skip if permission doesn't exist

                    # Assign facilitator to selected assessments
                    facilitator_assessments = form.cleaned_data[
                        "facilitator_assessments"
                    ]
                    for assessment in facilitator_assessments:
                        FacilitatorAssessmentAssignment.objects.create(
                            facilitator=user,
                            assessment=assessment,
                            assigned_by=request.user,
                        )

                    assessment_count = len(facilitator_assessments)
                    messages.success(
                        request,
                        f"Facilitator account '{username}' created and assigned to {assessment_count} assessment(s)!",
                    )

                elif account_type == "participant":
                    # Create WorkshopParticipantAccount
                    assessment = form.cleaned_data["assessment"]
                    province = form.cleaned_data["province"]
                    stakeholder_type = form.cleaned_data["stakeholder_type"]
                    office_business_name = form.cleaned_data.get(
                        "office_business_name", ""
                    )
                    municipality = form.cleaned_data.get("municipality")
                    barangay = form.cleaned_data.get("barangay")

                    # Determine region from province
                    region = province.region if province else None

                    WorkshopParticipantAccount.objects.create(
                        user=user,
                        assessment=assessment,
                        region=region,
                        province=province,
                        municipality=municipality,
                        barangay=barangay,
                        stakeholder_type=stakeholder_type,
                        office_business_name=office_business_name,
                        created_by=request.user,
                        current_workshop="workshop_1",
                        facilitator_advanced_to="workshop_1",
                    )

                    # Grant participant permission
                    permission = Permission.objects.get(
                        codename="can_access_regional_mana"
                    )
                    user.user_permissions.add(permission)

                    messages.success(
                        request,
                        f"Participant account '{username}' created and enrolled in assessment!",
                    )

                return redirect("mana:create_account")

            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AccountCreationForm()

    context = {
        "form": form,
    }
    return render(request, "mana/create_account.html", context)


@login_required
@facilitator_required
def facilitator_assessments_list(request):
    """List assessments assigned to this facilitator."""
    # Get assessments assigned to this facilitator
    assigned_assessment_ids = FacilitatorAssessmentAssignment.objects.filter(
        facilitator=request.user
    ).values_list("assessment_id", flat=True)

    assessments = (
        Assessment.objects.filter(id__in=assigned_assessment_ids)
        .select_related("province")
        .order_by("-planned_start_date")
    )

    assessments_data = []
    for assessment in assessments:
        # Get participant count
        total_participants = WorkshopParticipantAccount.objects.filter(
            assessment=assessment
        ).count()

        # Get workshop activities
        workshops = WorkshopActivity.objects.filter(assessment=assessment).order_by(
            "workshop_type"
        )

        # Calculate overall progress
        total_workshops = workshops.count()
        if total_workshops > 0 and total_participants > 0:
            total_possible_submissions = total_workshops * total_participants
            total_actual_submissions = 0

            for workshop in workshops:
                submitted_count = (
                    WorkshopResponse.objects.filter(
                        workshop=workshop, status="submitted"
                    )
                    .values("participant")
                    .distinct()
                    .count()
                )
                total_actual_submissions += submitted_count

            overall_progress = (
                (total_actual_submissions / total_possible_submissions * 100)
                if total_possible_submissions > 0
                else 0
            )
        else:
            overall_progress = 0

        # Determine status
        if overall_progress == 100:
            status = "completed"
        elif overall_progress > 0:
            status = "active"
        else:
            status = "not_started"

        assessments_data.append(
            {
                "assessment": assessment,
                "total_participants": total_participants,
                "total_workshops": total_workshops,
                "overall_progress": overall_progress,
                "status": status,
            }
        )

    context = {
        "assessments": assessments_data,
    }
    return render(request, "mana/facilitator/assessments_list.html", context)
