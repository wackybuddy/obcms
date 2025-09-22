from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from communities.models import OBCCommunity

from .models import (Assessment, AssessmentCategory, AssessmentTeamMember,
                     MANAReport, Need, NeedsCategory, Survey, WorkshopActivity,
                     WorkshopOutput, WorkshopParticipant, WorkshopSession)


@login_required
def new_assessment(request):
    """Create a new OBC-MANA assessment."""
    if request.method == "POST":
        try:
            with transaction.atomic():
                # Get form data
                title = request.POST.get("title")
                community_id = request.POST.get("community")
                primary_methodology = request.POST.get("primary_methodology")
                priority = request.POST.get("priority", "medium")
                assessment_level = request.POST.get("assessment_level", "community")
                planned_start_date = request.POST.get("planned_start_date")
                planned_end_date = request.POST.get("planned_end_date")
                objectives = request.POST.get("objectives")
                description = request.POST.get("description")
                estimated_budget = request.POST.get("estimated_budget")

                # Validate required fields
                if not all(
                    [
                        title,
                        community_id,
                        primary_methodology,
                        planned_start_date,
                        planned_end_date,
                        objectives,
                        description,
                    ]
                ):
                    messages.error(request, "Please fill in all required fields.")
                    return redirect("common:mana_new_assessment")

                # Get community
                community = get_object_or_404(OBCCommunity, id=community_id)

                # Get or create assessment category
                category, created = AssessmentCategory.objects.get_or_create(
                    name="OBC-MANA Workshop",
                    defaults={
                        "category_type": "needs_assessment",
                        "description": "Other Bangsamoro Communities Mapping and Needs Assessment",
                        "icon": "fas fa-users",
                        "color": "#3B82F6",
                    },
                )

                # Create assessment
                assessment = Assessment.objects.create(
                    title=title,
                    category=category,
                    description=description,
                    objectives=objectives,
                    assessment_level=assessment_level,
                    primary_methodology=primary_methodology,
                    community=community,
                    priority=priority,
                    planned_start_date=planned_start_date,
                    planned_end_date=planned_end_date,
                    estimated_budget=estimated_budget if estimated_budget else None,
                    lead_assessor=request.user,
                    created_by=request.user,
                )

                # Add team members
                team_leader_id = request.POST.get("team_leader")
                if team_leader_id:
                    AssessmentTeamMember.objects.create(
                        assessment=assessment,
                        user_id=team_leader_id,
                        role="team_leader",
                    )

                deputy_leader_id = request.POST.get("deputy_leader")
                if deputy_leader_id:
                    AssessmentTeamMember.objects.create(
                        assessment=assessment,
                        user_id=deputy_leader_id,
                        role="deputy_leader",
                    )

                primary_facilitator_id = request.POST.get("primary_facilitator")
                if primary_facilitator_id:
                    AssessmentTeamMember.objects.create(
                        assessment=assessment,
                        user_id=primary_facilitator_id,
                        role="facilitator",
                    )

                lead_documenter_id = request.POST.get("lead_documenter")
                if lead_documenter_id:
                    AssessmentTeamMember.objects.create(
                        assessment=assessment,
                        user_id=lead_documenter_id,
                        role="documenter",
                    )

                # If workshop methodology, create workshop activities
                if primary_methodology == "workshop":
                    create_workshop_activities(assessment, request.POST)

                messages.success(request, f'Assessment "{title}" created successfully!')
                return redirect("common:mana_manage_assessments")

        except Exception as e:
            messages.error(request, f"Error creating assessment: {str(e)}")
            return redirect("common:mana_new_assessment")

    # GET request - show form
    context = {
        "communities": OBCCommunity.objects.select_related(
            "barangay__municipality__province"
        ).all(),
        "users": User.objects.filter(is_active=True).order_by(
            "first_name", "last_name"
        ),
        "recent_assessments": Assessment.objects.select_related(
            "community__barangay"
        ).order_by("-created_at")[:5],
    }
    return render(request, "common/mana_new_assessment.html", context)


def create_workshop_activities(assessment, post_data):
    """Create the 6 core workshop activities for a workshop-based assessment."""

    start_date = datetime.strptime(
        post_data.get("planned_start_date"), "%Y-%m-%d"
    ).date()

    # Workshop definitions based on OBC-MANA guidelines
    workshops = [
        {
            "type": "workshop_1",
            "title": "Understanding the Community Context",
            "day": "day_2",
            "description": "Establish comprehensive understanding of OBC history, demographics, and socioeconomic conditions. Identify key strengths, resources, and assets within communities.",
            "methodology": "Small group discussions, participatory mapping, historical timeline development, stakeholder identification",
            "expected_outputs": "Community maps, historical timelines, inventory of community strengths, stakeholder maps",
            "duration": 4.0,
            "start_time": "09:00",
            "end_time": "13:00",
        },
        {
            "type": "workshop_2",
            "title": "Community Aspirations and Priorities",
            "day": "day_3",
            "description": "Document community vision for development. Identify key needs across social, economic, cultural, and rights dimensions. Prioritize sectors requiring immediate intervention.",
            "methodology": "Vision board creation, thematic small group discussions, structured prioritization exercises, plenary presentations",
            "expected_outputs": "Community vision statements, comprehensive needs assessment, prioritized list of development concerns",
            "duration": 4.0,
            "start_time": "09:00",
            "end_time": "13:00",
        },
        {
            "type": "workshop_3",
            "title": "Community Collaboration and Empowerment",
            "day": "day_3",
            "description": "Assess existing community organizations and leadership structures. Identify opportunities for strengthening collaboration and develop strategies for community empowerment.",
            "methodology": "Organizational mapping, collaboration assessment matrices, group work on empowerment strategies, action planning",
            "expected_outputs": "Map of community organizations, analysis of collaboration gaps, strategies for community capacity building",
            "duration": 4.0,
            "start_time": "14:00",
            "end_time": "18:00",
        },
        {
            "type": "workshop_4",
            "title": "Community Feedback on Existing Initiatives",
            "day": "day_4",
            "description": "Gather feedback on current government programs and services. Document successful interventions and lessons learned. Identify implementation challenges and gaps.",
            "methodology": "Program inventory development, small group program analysis, structured evaluation, recommendation formulation",
            "expected_outputs": "Inventory of programs with effectiveness assessment, documentation of best practices, analysis of implementation challenges",
            "duration": 3.0,
            "start_time": "09:00",
            "end_time": "12:00",
        },
        {
            "type": "workshop_5",
            "title": "OBCs Needs, Challenges, Factors, and Outcomes",
            "day": "day_4",
            "description": "Conduct in-depth analysis of priority issues. Explore root causes and contributing factors. Assess differential impacts on community segments.",
            "methodology": "Problem tree analysis, impact assessment matrices, factor relationship mapping, scenario development",
            "expected_outputs": "Problem trees for priority issues, analysis of impacts on different groups, relationship maps between factors",
            "duration": 3.0,
            "start_time": "13:00",
            "end_time": "16:00",
        },
        {
            "type": "workshop_6",
            "title": "Ways Forward and Action Planning",
            "day": "day_4",
            "description": "Develop potential community-led solutions. Identify roles for different stakeholders. Create preliminary action plans for priority issues.",
            "methodology": "Solution brainstorming, stakeholder role mapping, action planning templates, resource requirement identification",
            "expected_outputs": "Inventory of potential solutions, stakeholder role matrices, preliminary action plans, resource requirements",
            "duration": 2.0,
            "start_time": "16:00",
            "end_time": "18:00",
        },
    ]

    target_participants = int(post_data.get("target_participants", 30))

    for i, workshop_def in enumerate(workshops):
        # Calculate the date for each workshop
        if workshop_def["day"] == "day_2":
            workshop_date = start_date + timedelta(days=1)
        elif workshop_def["day"] == "day_3":
            workshop_date = start_date + timedelta(days=2)
        elif workshop_def["day"] == "day_4":
            workshop_date = start_date + timedelta(days=3)
        else:
            workshop_date = start_date

        WorkshopActivity.objects.create(
            assessment=assessment,
            workshop_type=workshop_def["type"],
            title=workshop_def["title"],
            description=workshop_def["description"],
            workshop_day=workshop_def["day"],
            scheduled_date=workshop_date,
            start_time=workshop_def["start_time"],
            end_time=workshop_def["end_time"],
            duration_hours=workshop_def["duration"],
            target_participants=target_participants,
            methodology=workshop_def["methodology"],
            expected_outputs=workshop_def["expected_outputs"],
            created_by=assessment.created_by,
        )


@login_required
def assessment_detail(request, assessment_id):
    """View detailed information about an assessment."""
    assessment = get_object_or_404(Assessment, id=assessment_id)

    context = {
        "assessment": assessment,
        "workshops": assessment.workshop_activities.all().order_by(
            "workshop_day", "start_time"
        ),
        "team_members": assessment.team_members.through.objects.filter(
            assessment=assessment
        ).select_related("user"),
        "can_edit": request.user == assessment.created_by
        or request.user == assessment.lead_assessor,
    }

    return render(request, "mana/assessment_detail.html", context)


@login_required
def workshop_detail(request, workshop_id):
    """View detailed information about a workshop."""
    workshop = get_object_or_404(WorkshopActivity, id=workshop_id)

    context = {
        "workshop": workshop,
        "sessions": workshop.sessions.all().order_by("session_order"),
        "participants": workshop.participants.all().order_by(
            "participant_type", "name"
        ),
        "outputs": workshop.outputs.all().order_by("output_type"),
        "can_edit": request.user == workshop.assessment.created_by
        or request.user in workshop.facilitators.all(),
    }

    return render(request, "mana/workshop_detail.html", context)


@login_required
def add_workshop_participant(request, workshop_id):
    """Add a participant to a workshop."""
    workshop = get_object_or_404(WorkshopActivity, id=workshop_id)

    if request.method == "POST":
        try:
            WorkshopParticipant.objects.create(
                workshop=workshop,
                name=request.POST.get("name"),
                participant_type=request.POST.get("participant_type"),
                gender=request.POST.get("gender"),
                age_group=request.POST.get("age_group"),
                contact_info=request.POST.get("contact_info", ""),
                organization=request.POST.get("organization", ""),
                attendance_status=request.POST.get("attendance_status", "attended"),
                participation_notes=request.POST.get("participation_notes", ""),
            )

            # Update actual participants count
            workshop.actual_participants = workshop.participants.count()
            workshop.save()

            messages.success(request, "Participant added successfully!")
        except Exception as e:
            messages.error(request, f"Error adding participant: {str(e)}")

    return redirect("mana:workshop_detail", workshop_id=workshop_id)


@login_required
def add_workshop_output(request, workshop_id):
    """Add an output to a workshop."""
    workshop = get_object_or_404(WorkshopActivity, id=workshop_id)

    if request.method == "POST":
        try:
            WorkshopOutput.objects.create(
                workshop=workshop,
                output_type=request.POST.get("output_type"),
                title=request.POST.get("title"),
                description=request.POST.get("description"),
                content=request.POST.get("content"),
                file_path=request.POST.get("file_path", ""),
                created_by=request.user,
            )

            messages.success(request, "Workshop output added successfully!")
        except Exception as e:
            messages.error(request, f"Error adding output: {str(e)}")

    return redirect("mana:workshop_detail", workshop_id=workshop_id)


@login_required
def generate_mana_report(request, assessment_id):
    """Generate or view the MANA report for an assessment."""
    assessment = get_object_or_404(Assessment, id=assessment_id)

    # Get or create the MANA report
    report, created = MANAReport.objects.get_or_create(
        assessment=assessment,
        defaults={
            "title": f"OBC-MANA Report - {assessment.community.barangay.name} - {assessment.created_at.year}",
            "created_by": request.user,
        },
    )

    if request.method == "POST":
        # Update report content
        report.executive_summary = request.POST.get("executive_summary", "")
        report.context_background = request.POST.get("context_background", "")
        report.methodology = request.POST.get("methodology", "")
        report.social_development_findings = request.POST.get(
            "social_development_findings", ""
        )
        report.economic_development_findings = request.POST.get(
            "economic_development_findings", ""
        )
        report.cultural_development_findings = request.POST.get(
            "cultural_development_findings", ""
        )
        report.rights_protection_findings = request.POST.get(
            "rights_protection_findings", ""
        )
        report.priority_issues = request.POST.get("priority_issues", "")
        report.policy_recommendations = request.POST.get("policy_recommendations", "")
        report.program_development_opportunities = request.POST.get(
            "program_development_opportunities", ""
        )
        report.strategic_approaches = request.POST.get("strategic_approaches", "")
        report.stakeholder_roles = request.POST.get("stakeholder_roles", "")
        report.resource_requirements = request.POST.get("resource_requirements", "")
        report.monitoring_evaluation = request.POST.get("monitoring_evaluation", "")

        # Update status if provided
        new_status = request.POST.get("report_status")
        if new_status:
            report.report_status = new_status

        report.save()
        messages.success(request, "MANA report updated successfully!")
        return redirect("mana:generate_mana_report", assessment_id=assessment_id)

    context = {
        "assessment": assessment,
        "report": report,
        "workshops": assessment.workshop_activities.all().order_by("workshop_day"),
        "can_edit": request.user == assessment.created_by
        or request.user == assessment.lead_assessor,
    }

    return render(request, "mana/mana_report.html", context)
