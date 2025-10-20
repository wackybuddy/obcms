"""
OCM (Office of the Chief Minister) aggregation views.

These views expose read-only dashboards that aggregate data across all
organizations. They provide enough context for templates while keeping the
computation light for development and test environments.
"""

from __future__ import annotations

import json
from collections import Counter
from decimal import Decimal
from typing import Iterable, List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from budget_execution.models.allotment import Allotment
from budget_execution.models.disbursement import Disbursement
from budget_preparation.models.budget_proposal import BudgetProposal
from budget_preparation.models.program_budget import ProgramBudget
from coordination.models import InterMOAPartnership
from organizations.models import Organization
from planning.models import AnnualWorkPlan, StrategicPlan

BILLION = Decimal("1000000000")


def _to_billions(amount: Decimal | float | None) -> Decimal:
    """Convert a peso amount to billions with two decimal precision."""
    if not amount:
        return Decimal("0.00")
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    return (amount / BILLION).quantize(Decimal("0.01"))


def _safe_percentage(numerator: Decimal | float, denominator: Decimal | float) -> float:
    """Return a safe percentage value rounded to one decimal place."""
    if not denominator:
        return 0.0
    return round(float(numerator) / float(denominator) * 100, 1)


def _average(values: Iterable[float | Decimal]) -> float:
    """Compute the average of an iterable of numeric values."""
    values = [float(value) for value in values if value is not None]
    if not values:
        return 0.0
    return round(sum(values) / len(values), 1)


def _organization_map() -> dict[str, Organization]:
    """Return a cached map of organization code → organization object."""
    return {org.code: org for org in Organization.objects.all()}


class OCMBaseView(LoginRequiredMixin, TemplateView):
    """Base view that enforces authentication and shared helpers."""

    login_url = "common:login"
    redirect_field_name = "next"

    @cached_property
    def org_map(self) -> dict[str, Organization]:
        return _organization_map()

    @cached_property
    def organizations(self) -> List[dict[str, str]]:
        """Return organizations as dictionaries usable in templates."""
        orgs = []
        for org in Organization.objects.order_by("code"):
            orgs.append(
                {
                    "instance": org,
                    "code": org.code,
                    "name": org.name,
                    "short_name": org.acronym or org.name,
                }
            )
        return orgs


class DashboardView(OCMBaseView):
    template_name = "ocm/dashboard/main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "stats": self._build_stats(),
                "metrics": self._build_metrics(),
                "moas": self.organizations,
            }
        )
        return context

    def _build_stats(self) -> dict[str, float | int]:
        proposals = BudgetProposal.objects.all()
        approved_total = proposals.aggregate(total=Sum("total_approved_budget"))["total"]
        requested_total = proposals.aggregate(total=Sum("total_requested_budget"))["total"]

        total_budget = approved_total or requested_total or Decimal("0")

        return {
            "total_moas": len(self.organizations),
            "total_budget": float(_to_billions(total_budget)),
            "strategic_plans": StrategicPlan.objects.count(),
            "partnerships": InterMOAPartnership.objects.count(),
        }

    def _build_metrics(self) -> dict[str, float]:
        proposals = BudgetProposal.objects.all()
        total_proposals = proposals.count()
        approved_count = proposals.filter(status="approved").count()

        work_plans = AnnualWorkPlan.objects.all()
        completion_values = [plan.overall_progress for plan in work_plans]

        partnerships = InterMOAPartnership.objects.all()
        completed_count = partnerships.filter(status="completed").count()

        return {
            "budget_approval_rate": _safe_percentage(approved_count, total_proposals),
            "planning_completion": _average(completion_values),
            "partnership_success": _safe_percentage(completed_count, partnerships.count()),
        }


class ConsolidatedBudgetView(OCMBaseView):
    template_name = "ocm/budget/consolidated.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        summaries = self._build_budget_summaries()

        total_proposed = sum(item["proposed"] for item in summaries)
        total_approved = sum(item["approved"] for item in summaries)
        total_allocated = sum(item["allocated"] for item in summaries)
        total_disbursed = sum(item["disbursed"] for item in summaries)

        variance_flagged = (
            ProgramBudget.objects.filter(approved_amount__isnull=False)
            .exclude(approved_amount=F("requested_amount"))
            .count()
        )

        context.update(
            {
                "budget": {
                    "total_proposed": float(_to_billions(total_proposed)),
                    "total_approved": float(_to_billions(total_approved)),
                    "approval_rate": _safe_percentage(total_approved, total_proposed),
                    "utilization_rate": _safe_percentage(total_disbursed, total_allocated),
                    "variance_flagged": variance_flagged,
                },
                "budget_items": summaries,
                "chart_data": {
                    "moa_labels": json.dumps([item["organization"].code for item in summaries]),
                    "proposed_amounts": json.dumps([float(item["proposed"]) for item in summaries]),
                    "approved_amounts": json.dumps([float(item["approved"]) for item in summaries]),
                    "utilization_data": json.dumps(
                        [
                            float(total_disbursed),
                            float(max(total_allocated - total_disbursed, Decimal("0"))),
                        ]
                    ),
                },
            }
        )
        return context

    def _build_budget_summaries(self) -> list[dict]:
        summaries: list[dict] = []

        for org_entry in self.organizations:
            org = org_entry["instance"]
            org_proposals = BudgetProposal.objects.filter(organization=org)

            proposed = org_proposals.aggregate(total=Sum("total_requested_budget"))["total"] or Decimal("0")
            approved = org_proposals.aggregate(total=Sum("total_approved_budget"))["total"] or Decimal("0")

            allocated = (
                Allotment.objects.filter(program_budget__budget_proposal__organization=org).aggregate(
                    total=Sum("amount")
                )["total"]
                or Decimal("0")
            )
            disbursed = (
                Disbursement.objects.filter(
                    obligation__allotment__program_budget__budget_proposal__organization=org
                ).aggregate(total=Sum("amount"))["total"]
                or Decimal("0")
            )

            summaries.append(
                {
                    "organization": org,
                    "proposed": proposed,
                    "approved": approved,
                    "allocated": allocated,
                    "disbursed": disbursed,
                    "utilization_rate": _safe_percentage(disbursed, allocated),
                }
            )

        return summaries


class PlanningOverviewView(OCMBaseView):
    template_name = "ocm/planning/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        plans = StrategicPlan.objects.all()
        planning_summary = {
            "total": plans.count(),
            "active": plans.filter(status="active").count(),
            "completed": plans.filter(status="completed").count(),
        }

        planning_summary["completion_rate"] = self._compute_completion_rate()

        planning_by_moa = self._build_planning_by_moa()

        context.update(
            {
                "planning": planning_summary,
                "planning_by_moa": planning_by_moa,
                "chart_data": {
                    "moa_labels": json.dumps([item["code"] for item in planning_by_moa]),
                    "completion_rates": json.dumps([item["completion_rate"] for item in planning_by_moa]),
                },
            }
        )
        return context

    def _compute_completion_rate(self) -> float:
        plans = AnnualWorkPlan.objects.all()
        completion_values = [plan.overall_progress for plan in plans]
        return _average(completion_values)

    def _build_planning_by_moa(self) -> list[dict]:
        """
        Build planning metrics per organization.

        BMMS multi-tenant fields are still being rolled out for the planning app,
        so we approximate MOA coverage by following ProgramBudget relationships.
        """
        results: list[dict] = []

        for org_entry in self.organizations:
            org = org_entry["instance"]
            related_plans = (
                AnnualWorkPlan.objects.filter(program_budgets__budget_proposal__organization=org)
                .distinct()
                .prefetch_related("program_budgets")
            )
            if not related_plans.exists():
                continue

            completion_values = [plan.overall_progress for plan in related_plans]

            results.append(
                {
                    "code": org_entry["code"],
                    "short_name": org_entry["short_name"],
                    "active": related_plans.filter(status__in=["active", "approved"]).count(),
                    "completed": related_plans.filter(status="completed").count(),
                    "completion_rate": _average(completion_values),
                }
            )

        return results


class CoordinationMatrixView(OCMBaseView):
    template_name = "ocm/coordination/matrix.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partnerships = InterMOAPartnership.objects.all()

        coordination_summary = {
            "total": partnerships.count(),
            "active": partnerships.filter(status="active").count(),
            "successful": partnerships.filter(status="completed").count(),
        }
        coordination_summary["success_rate"] = _safe_percentage(
            coordination_summary["successful"], coordination_summary["total"]
        )

        partnership_rows = [self._serialize_partnership(partnership) for partnership in partnerships]
        most_collaborative = self._most_collaborative(partnership_rows)

        context.update(
            {
                "coordination": coordination_summary,
                "partnerships": partnership_rows,
                "most_collaborative": most_collaborative,
                "moas": self.organizations,
            }
        )
        return context

    def _serialize_partnership(self, partnership: InterMOAPartnership) -> dict:
        org_map = self.org_map
        lead = org_map.get(partnership.lead_moa_code)
        partners = [org_map.get(code) for code in partnership.participating_moa_codes]

        partners_clean = [partner for partner in partners if partner is not None]

        return {
            "id": partnership.pk,
            "name": partnership.title,
            "status": partnership.status,
            "focus_area": partnership.partnership_type,
            "progress": partnership.progress_percentage,
            "lead_moa": lead,
            "partners": partners_clean,
        }

    def _most_collaborative(self, partnerships: list[dict]) -> list[dict]:
        counter = Counter()

        for entry in partnerships:
            lead = entry.get("lead_moa")
            if lead:
                counter[lead.code] += 1
            for partner in entry.get("partners", []):
                counter[partner.code] += 1

        ranked = counter.most_common(5)
        results = []
        for code, total in ranked:
            org = self.org_map.get(code)
            if not org:
                continue
            results.append(
                {
                    "organization": org,
                    "total": total,
                    "active": entry_count(org, partnerships, status_filter="active"),
                }
            )
        return results


class PerformanceOverviewView(OCMBaseView):
    template_name = "ocm/performance/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        budget_metrics = self._budget_metrics()
        planning_metrics = self._planning_metrics()
        partnership_metrics = self._partnership_metrics()

        performance = {
            "overall_score": round(
                (
                    budget_metrics["budget_efficiency"]
                    + planning_metrics["execution_progress"]
                    + partnership_metrics["collaboration_score"]
                )
                / 3,
                1,
            ),
            "budget_efficiency": budget_metrics["budget_efficiency"],
            "execution_progress": planning_metrics["execution_progress"],
            "collaboration_index": partnership_metrics["collaboration_score"],
            "stakeholder_satisfaction": partnership_metrics["stakeholder_score"],
        }

        context.update(
            {
                "performance": performance,
                "moas": self.organizations,
            }
        )
        return context

    def _budget_metrics(self) -> dict[str, float]:
        proposals = BudgetProposal.objects.all()
        requested = proposals.aggregate(total=Sum("total_requested_budget"))["total"] or Decimal("0")
        approved = proposals.aggregate(total=Sum("total_approved_budget"))["total"] or Decimal("0")
        return {"budget_efficiency": _safe_percentage(approved, requested)}

    def _planning_metrics(self) -> dict[str, float]:
        work_plans = AnnualWorkPlan.objects.all()
        completion_values = [plan.overall_progress for plan in work_plans]
        return {"execution_progress": _average(completion_values)}

    def _partnership_metrics(self) -> dict[str, float]:
        partnerships = InterMOAPartnership.objects.all()
        total = partnerships.count()
        active = partnerships.filter(status="active").count()
        completed = partnerships.filter(status="completed").count()

        collaboration_score = _safe_percentage(active + completed, total)
        stakeholder_score = _safe_percentage(completed, total)

        return {
            "collaboration_score": collaboration_score,
            "stakeholder_score": stakeholder_score,
        }


class ReportsView(OCMBaseView):
    template_name = "ocm/reports/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["moas"] = self.organizations
        return context


def entry_count(org: Organization, partnerships: list[dict], status_filter: str | None = None) -> int:
    """Helper for counting partnerships per organization with optional status filter."""
    count = 0
    for entry in partnerships:
        participants = []
        lead = entry.get("lead_moa")
        if lead:
            participants.append(lead)
        participants.extend(entry.get("partners", []))

        if status_filter and entry.get("status") != status_filter:
            continue

        count += sum(1 for participant in participants if participant and participant.code == org.code)
    return count
