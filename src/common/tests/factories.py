"""Test factories for creating minimal domain objects needed by task tests."""

from __future__ import annotations

import uuid
from datetime import date, time, timedelta
from decimal import Decimal

from django.utils import timezone

from common.models import (
    Barangay,
    Municipality,
    Province,
    Region,
)
from communities.models import OBCCommunity, Stakeholder
from coordination.models import Event, Organization, Partnership
from mana.models import Assessment, AssessmentCategory, BaselineStudy, WorkshopActivity
from recommendations.policy_tracking.models import (
    PolicyImplementationMilestone,
    PolicyRecommendation,
)
from services.models import ServiceApplication, ServiceOffering


def _unique_suffix() -> str:
    return uuid.uuid4().hex[:6]


def create_region(code: str | None = None, name: str | None = None) -> Region:
    code = code or f"RG{_unique_suffix()}"
    name = name or f"Region {code}"
    return Region.objects.create(code=code, name=name)


def create_province(
    region: Region | None = None,
    code: str | None = None,
    name: str | None = None,
) -> Province:
    region = region or create_region()
    code = code or f"PR{_unique_suffix()}"
    name = name or f"Province {code}"
    return Province.objects.create(region=region, code=code, name=name)


def create_municipality(
    province: Province | None = None,
    code: str | None = None,
    name: str | None = None,
) -> Municipality:
    province = province or create_province()
    code = code or f"MU{_unique_suffix()}"
    name = name or f"Municipality {code}"
    return Municipality.objects.create(province=province, code=code, name=name)


def create_barangay(
    municipality: Municipality | None = None,
    code: str | None = None,
    name: str | None = None,
) -> Barangay:
    municipality = municipality or create_municipality()
    code = code or f"BR{_unique_suffix()}"
    name = name or f"Barangay {code}"
    return Barangay.objects.create(municipality=municipality, code=code, name=name)


def create_community(name: str | None = None) -> OBCCommunity:
    barangay = create_barangay()
    name = name or f"Community {barangay.code}"
    return OBCCommunity.objects.create(barangay=barangay, name=name)


def create_stakeholder(
    *,
    community: OBCCommunity | None = None,
    full_name: str | None = None,
    stakeholder_type: str = "community_leader",
) -> Stakeholder:
    community = community or create_community()
    full_name = full_name or f"Stakeholder { _unique_suffix() }"
    return Stakeholder.objects.create(
        full_name=full_name,
        stakeholder_type=stakeholder_type,
        community=community,
    )


def create_assessment_category(
    name: str | None = None,
    category_type: str = "needs_assessment",
) -> AssessmentCategory:
    name = name or f"Category { _unique_suffix() }"
    return AssessmentCategory.objects.create(
        name=name,
        category_type=category_type,
    )


def create_assessment(
    *,
    created_by,
    title: str | None = None,
    category: AssessmentCategory | None = None,
    lead_assessor=None,
    planned_start: date | None = None,
    planned_end: date | None = None,
    **overrides,
) -> Assessment:
    category = category or create_assessment_category()
    title = title or f"Assessment { _unique_suffix() }"
    planned_start = planned_start or date.today()
    planned_end = planned_end or date.today()
    lead_assessor = lead_assessor or created_by
    defaults = {
        "title": title,
        "category": category,
        "description": "Assessment description",
        "objectives": "Assessment objectives",
        "assessment_level": "community",
        "primary_methodology": overrides.pop("primary_methodology", "survey"),
        "planned_start_date": planned_start,
        "planned_end_date": planned_end,
        "lead_assessor": lead_assessor,
        "created_by": created_by,
        "status": overrides.pop("status", "planning"),
        "priority": overrides.pop("priority", "medium"),
    }
    defaults.update(overrides)
    return Assessment.objects.create(**defaults)


def create_event(
    *,
    created_by,
    organizer=None,
    title: str | None = None,
    event_type: str = "meeting",
    start_date: date | None = None,
    **overrides,
) -> Event:
    organizer = organizer or created_by
    title = title or f"Event { _unique_suffix() }"
    start_date = start_date or date.today()
    defaults = {
        "title": title,
        "event_type": event_type,
        "description": "Event description",
        "status": overrides.pop("status", "planned"),
        "priority": overrides.pop("priority", "medium"),
        "start_date": start_date,
        "venue": overrides.pop("venue", "Main Hall"),
        "address": overrides.pop("address", "123 Test Street"),
        "organizer": organizer,
        "created_by": created_by,
    }
    defaults.update(overrides)
    return Event.objects.create(**defaults)


def create_organization(
    name: str | None = None,
    organization_type: str = "ngo",
) -> Organization:
    name = name or f"Organization { _unique_suffix() }"
    return Organization.objects.create(name=name, organization_type=organization_type)


def create_partnership(
    *,
    created_by,
    lead_organization: Organization | None = None,
    title: str | None = None,
    partnership_type: str = "moa",
    **overrides,
) -> Partnership:
    lead_organization = lead_organization or create_organization()
    title = title or f"Partnership { _unique_suffix() }"
    defaults = {
        "title": title,
        "partnership_type": partnership_type,
        "description": "Partnership description",
        "objectives": "Partnership objectives",
        "scope": "Partnership scope",
        "lead_organization": lead_organization,
        "created_by": created_by,
    }
    defaults.update(overrides)
    partnership = Partnership.objects.create(**defaults)
    partnership.organizations.add(lead_organization)
    return partnership


def create_policy_recommendation(
    *,
    proposed_by,
    title: str | None = None,
    category: str = "economic_development",
    scope: str = "regional",
    **overrides,
) -> PolicyRecommendation:
    title = title or f"Policy { _unique_suffix() }"
    defaults = {
        "title": title,
        "category": category,
        "description": "Policy description",
        "rationale": "Policy rationale",
        "scope": scope,
        "proposed_by": proposed_by,
        "problem_statement": "Problem statement",
        "policy_objectives": "Policy objectives",
        "proposed_solution": "Proposed solution",
        "expected_outcomes": "Expected outcomes",
        "status": overrides.pop("status", "draft"),
        "priority": overrides.pop("priority", "medium"),
    }
    defaults.update(overrides)
    return PolicyRecommendation.objects.create(**defaults)


def create_policy_milestone(
    *,
    policy: PolicyRecommendation,
    created_by,
    title: str | None = None,
    target_date: date | None = None,
    **overrides,
) -> PolicyImplementationMilestone:
    title = title or f"Milestone { _unique_suffix() }"
    target_date = target_date or date.today()
    defaults = {
        "policy": policy,
        "title": title,
        "description": "Milestone description",
        "target_date": target_date,
        "responsible_party": "Implementation Unit",
        "created_by": created_by,
    }
    defaults.update(overrides)
    return PolicyImplementationMilestone.objects.create(**defaults)


def create_baseline_study(
    *,
    assessment: Assessment,
    community: OBCCommunity,
    principal_investigator,
    created_by,
    title: str | None = None,
    planned_start: date | None = None,
    planned_end: date | None = None,
    **overrides,
) -> BaselineStudy:
    title = title or f"Baseline { _unique_suffix() }"
    planned_start = planned_start or date.today()
    planned_end = planned_end or (planned_start + timedelta(days=30))
    defaults = {
        "title": title,
        "study_type": overrides.pop("study_type", "comprehensive"),
        "description": "Baseline description",
        "objectives": "Baseline objectives",
        "community": community,
        "assessment": assessment,
        "methodology": overrides.pop("methodology", "mixed_methods"),
        "planned_start_date": planned_start,
        "planned_end_date": planned_end,
        "principal_investigator": principal_investigator,
        "data_collection_methods": "Methods",
        "study_domains": {"domains": ["education"]},
        "geographic_coverage": "Coverage",
        "target_population": "Target population",
        "created_by": created_by,
    }
    defaults.update(overrides)
    return BaselineStudy.objects.create(**defaults)


def create_workshop_activity(
    *,
    assessment: Assessment,
    created_by,
    workshop_type: str = "workshop_1",
    scheduled_date: date | None = None,
    **overrides,
) -> WorkshopActivity:
    scheduled_date = scheduled_date or date.today()
    defaults = {
        "assessment": assessment,
        "workshop_type": workshop_type,
        "title": overrides.pop("title", f"Workshop { _unique_suffix() }"),
        "description": "Workshop description",
        "workshop_day": overrides.pop("workshop_day", "day_2"),
        "status": overrides.pop("status", "planned"),
        "scheduled_date": scheduled_date,
        "start_time": overrides.pop("start_time", time(9, 0)),
        "end_time": overrides.pop("end_time", time(12, 0)),
        "duration_hours": overrides.pop("duration_hours", 3.0),
        "target_participants": overrides.pop("target_participants", 25),
        "methodology": overrides.pop("methodology", "Participatory methods"),
        "expected_outputs": overrides.pop("expected_outputs", "Workshop outputs"),
        "created_by": created_by,
    }
    defaults.update(overrides)
    workshop = WorkshopActivity.objects.create(**defaults)
    workshop.facilitators.add(created_by)
    return workshop


def create_service_offering(
    *,
    created_by,
    offering_mao: Organization | None = None,
    title: str | None = None,
    service_type: str = "training",
    **overrides,
) -> ServiceOffering:
    offering_mao = offering_mao or create_organization(
        name="MAO", organization_type="bmoa"
    )
    title = title or f"Service { _unique_suffix() }"
    defaults = {
        "title": title,
        "service_type": service_type,
        "description": "Service description",
        "objectives": "Service objectives",
        "offering_mao": offering_mao,
        "eligibility_level": overrides.pop("eligibility_level", "community"),
        "eligibility_criteria": "Eligibility criteria",
        "status": overrides.pop("status", "active"),
        "application_process": "Process",
        "contact_information": "Contact",
        "created_by": created_by,
    }
    defaults.update(overrides)
    return ServiceOffering.objects.create(**defaults)


def create_service_application(
    *,
    service: ServiceOffering,
    applicant_user,
    applicant_name: str | None = None,
    status: str = "submitted",
    **overrides,
) -> ServiceApplication:
    applicant_name = applicant_name or f"Applicant { _unique_suffix() }"
    defaults = {
        "service": service,
        "applicant_user": applicant_user,
        "applicant_name": applicant_name,
        "application_details": overrides.pop(
            "application_details", "Application details"
        ),
        "status": status,
        "submission_date": overrides.pop("submission_date", timezone.now()),
    }
    defaults.update(overrides)
    return ServiceApplication.objects.create(**defaults)


def create_monitoring_entry(
    *,
    created_by,
    title: str | None = None,
    category: str = "moa_ppa",
    start_date: date | None = None,
    **overrides,
):
    from monitoring.models import MonitoringEntry

    title = title or f"Monitoring Entry { _unique_suffix() }"
    start_date = start_date or date.today()
    budget_value = overrides.pop(
        "budget_allocation",
        overrides.pop("budget_allocated", Decimal("1000000.00")),
    )

    defaults = {
        "title": title,
        "category": category,
        "start_date": start_date,
        "budget_allocation": budget_value,
        "created_by": created_by,
    }
    defaults.update(overrides)
    return MonitoringEntry.objects.create(**defaults)
