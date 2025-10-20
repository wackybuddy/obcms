"""Seed demo data for budget preparation E2E flows."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from budget_preparation.models.budget_proposal import BudgetProposal
from budget_preparation.services.budget_builder import BudgetBuilderService
from organizations.models import Organization


class Command(BaseCommand):
    help = "Create a demo budget proposal with program and line item for E2E tests"

    def handle(self, *args, **options):
        organization = Organization.objects.filter(code="OOBC").first()
        if organization is None:
            organization = Organization.objects.order_by("code").first()

        if organization is None:
            self.stderr.write(self.style.ERROR("No organizations available to seed demo data."))
            return

        User = get_user_model()
        user = User.objects.filter(username="playwright").first() or User.objects.filter(is_superuser=True).first()

        current_year = timezone.now().year
        fiscal_year = current_year + 1

        proposal, created = BudgetProposal.objects.get_or_create(
            organization=organization,
            fiscal_year=fiscal_year,
            defaults={
                "title": "Demo Budget Proposal",
                "description": "Automatically generated for end-to-end testing workflows.",
                "submitted_by": user,
                "total_requested_budget": Decimal("0.00"),
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created demo proposal for FY {fiscal_year}."))
        else:
            self.stdout.write(self.style.WARNING(f"Reusing existing demo proposal for FY {fiscal_year}."))

        service = BudgetBuilderService()

        if not proposal.program_budgets.exists():
            program_budget = service.add_program_budget(
                proposal=proposal,
                monitoring_entry=None,
                requested_amount=Decimal("150000000"),
                priority_rank=1,
                justification="Seeded program budget to exercise UI workflows.",
                expected_outcomes="Baseline program outcomes for testing.",
            )
            self.stdout.write(self.style.SUCCESS("Added demo program budget."))
        else:
            program_budget = proposal.program_budgets.first()

        if program_budget and not program_budget.line_items.exists():
            service.add_line_item(
                program_budget=program_budget,
                category="operating",
                description="Demo operating expenses",
                unit_cost=Decimal("5000000"),
                quantity=3,
                justification="Seed data to validate line item flows.",
                notes="Auto-generated seed data",
            )
            self.stdout.write(self.style.SUCCESS("Added demo line item."))

        service._update_proposal_total(proposal)
        self.stdout.write(self.style.SUCCESS("Demo budget data ready."))
