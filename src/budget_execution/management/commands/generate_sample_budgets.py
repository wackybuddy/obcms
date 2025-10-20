"""Generate budget execution sample data for pilot MOAs."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from organizations.models import Organization
from planning.models import WorkPlanObjective
from budget_preparation.models import BudgetProposal, ProgramBudget
from budget_execution.models import Allotment, Obligation, Disbursement

UserModel = get_user_model()


class Command(BaseCommand):
    help = "Generate budget proposal, program budgets, and execution entries for a pilot organization"

    def add_arguments(self, parser):  # type: ignore[override]
        parser.add_argument("--organization", required=True, help="Organization code (e.g., MOH)")
        parser.add_argument("--year", type=int, default=date.today().year)
        parser.add_argument("--programs", type=int, default=3, help="Number of objectives to convert into budgets")

    @transaction.atomic
    def handle(self, *args, **options):  # type: ignore[override]
        code = options["organization"]
        try:
            organization = Organization.objects.get(code__iexact=code)
        except Organization.DoesNotExist as exc:
            raise CommandError("Organization not found. Run load_pilot_moas first.") from exc

        created_by = UserModel.objects.filter(is_superuser=True).first() or UserModel.objects.first()
        if not created_by:
            raise CommandError("At least one user is required to create budget entries")

        # Ensure planning data exists
        objectives = (
            WorkPlanObjective.objects.filter(
                annual_work_plan__strategic_plan__title__icontains=organization.name
            )
            .order_by("target_date")
        )
        if not objectives.exists():
            call_command("generate_sample_programs", organization=code, programs=options["programs"], year=options["year"])
            objectives = (
                WorkPlanObjective.objects.filter(
                    annual_work_plan__strategic_plan__title__icontains=organization.name
                )
                .order_by("target_date")
            )

        objectives = list(objectives[: options["programs"]])
        if not objectives:
            raise CommandError("No work plan objectives available to budget against")

        proposal, _ = BudgetProposal.objects.get_or_create(
            organization=organization,
            fiscal_year=options["year"],
            defaults={
                "title": f"{organization.name} Budget Proposal {options['year']}",
                "description": "Auto-generated pilot budget proposal",
                "total_requested_budget": Decimal("0.00"),
                "status": "submitted",
                "submitted_by": created_by,
            },
        )

        total_allocated = Decimal("0.00")
        for index, objective in enumerate(objectives, start=1):
            allocated_amount = Decimal("1000000.00") + Decimal(index * 50000)
            program_budget, created = ProgramBudget.objects.get_or_create(
                budget_proposal=proposal,
                program=objective,
                defaults={
                    "requested_amount": allocated_amount,
                    "approved_amount": allocated_amount,
                    "priority_rank": index,
                    "priority_level": "high" if index == 1 else "medium",
                    "justification": f"Fund initiative {objective.title}",
                    "expected_outputs": "Service delivery milestones",
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created program budget for {objective.title} (₱{allocated_amount:,.2f})"
                    )
                )
            if created:
                program_budget.approved_amount = allocated_amount
                program_budget.save(update_fields=["approved_amount", "updated_at"])

            total_allocated += program_budget.requested_amount

            quarterly_amount = (program_budget.approved_amount or program_budget.requested_amount) / Decimal("4")
            for quarter in range(1, 5):
                allotment, _ = Allotment.objects.get_or_create(
                    program_budget=program_budget,
                    quarter=quarter,
                    defaults={
                        "amount": quarterly_amount,
                        "status": "released" if quarter <= 2 else "pending",
                        "release_date": date(options["year"], min(12, quarter * 3), 15),
                        "created_by": created_by,
                    },
                )

                obligation_amount = (allotment.amount * Decimal("0.6")).quantize(Decimal("0.01"))
                obligation, _ = Obligation.objects.get_or_create(
                    allotment=allotment,
                    description=f"Obligation for {objective.title} Q{quarter}",
                    defaults={
                        "amount": obligation_amount,
                        "obligated_date": date(options["year"], min(12, quarter * 3), 20),
                        "created_by": created_by,
                    },
                )

                disbursement_amount = (obligation.amount * Decimal("0.5")).quantize(Decimal("0.01"))
                Disbursement.objects.get_or_create(
                    obligation=obligation,
                    amount=disbursement_amount,
                    disbursed_date=date(options["year"], min(12, quarter * 3), 25),
                    payee=f"{organization.acronym} Supplier",
                    defaults={
                        "created_by": created_by,
                        "payment_method": "check",
                    },
                )

        proposal.total_proposed_budget = total_allocated
        proposal.total_approved_budget = total_allocated
        proposal.save(update_fields=["total_requested_budget", "total_approved_budget", "updated_at"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Budget data generated for {organization.code} ({len(objectives)} objectives)"
            )
        )
