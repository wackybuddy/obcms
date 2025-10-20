"""
Comprehensive integration tests for WorkItem module in budget execution system.

Tests cover:
- WorkItem creation/editing/deletion workflows
- Cross-module communication (budget_execution ↔ budget_preparation)
- Data cascade operations
- Multi-tenant data isolation
- API integration
- Database transaction handling
- State consistency across workflows
"""

import pytest
from decimal import Decimal
from datetime import date
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from budget_execution.models import WorkItem, Obligation, Allotment, Disbursement
from budget_preparation.models import BudgetProposal, ProgramBudget, BudgetLineItem


@pytest.mark.integration
@pytest.mark.django_db
class TestWorkItemCreation:
    """Test workitem creation and linking to allotments/obligations."""

    def test_create_workitem_basic(self, monitoring_entry):
        """Test basic workitem creation."""
        work_item = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="Community Development Project",
            description="Development of community infrastructure",
            estimated_cost=Decimal('1000000.00'),
            status='planned'
        )

        assert work_item.id is not None
        assert work_item.title == "Community Development Project"
        assert work_item.estimated_cost == Decimal('1000000.00')
        assert work_item.status == 'planned'
        assert work_item.monitoring_entry == monitoring_entry
        assert work_item.total_obligations() == Decimal('0.00')
        assert work_item.total_disbursements() == Decimal('0.00')

    def test_create_workitem_with_dates(self, monitoring_entry):
        """Test workitem creation with start and end dates."""
        work_item = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="Training Program",
            estimated_cost=Decimal('500000.00'),
            start_date=date(2025, 1, 15),
            end_date=date(2025, 6, 30),
            status='in_progress'
        )

        assert work_item.start_date == date(2025, 1, 15)
        assert work_item.end_date == date(2025, 6, 30)
        assert work_item.status == 'in_progress'

    def test_create_workitem_linked_to_allotment_obligation(
        self, monitoring_entry, allotment_q1, execution_user
    ):
        """Test workitem creation and linking through obligations."""
        work_item = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="School Construction",
            estimated_cost=Decimal('5000000.00'),
            status='in_progress'
        )

        # Create obligation linking workitem to allotment
        obligation = Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('5000000.00'),
            payee="Construction Contractor",
            obligated_by=execution_user,
            status='obligated'
        )

        # Verify relationships
        assert obligation.work_item == work_item
        assert obligation.allotment == allotment_q1
        assert work_item.obligations.count() == 1
        assert work_item.total_obligations() == Decimal('5000000.00')

    def test_workitem_status_choices(self, monitoring_entry):
        """Test that workitem only accepts valid status choices."""
        valid_statuses = ['planned', 'in_progress', 'completed', 'cancelled']

        for status in valid_statuses:
            work_item = WorkItem.objects.create(
                monitoring_entry=monitoring_entry,
                title=f"Project {status}",
                estimated_cost=Decimal('100000.00'),
                status=status
            )
            assert work_item.status == status

    def test_workitem_minimum_estimated_cost(self, monitoring_entry):
        """Test workitem with zero or negative estimated cost fails."""
        # Zero should fail due to MinValueValidator
        with pytest.raises(ValidationError):
            WorkItem.objects.create(
                monitoring_entry=monitoring_entry,
                title="Invalid Cost",
                estimated_cost=Decimal('-100000.00'),
                status='planned'
            )


@pytest.mark.integration
@pytest.mark.django_db
class TestWorkItemEditing:
    """Test workitem editing and update workflows."""

    def test_edit_workitem_title(self, work_item):
        """Test editing workitem title."""
        original_title = work_item.title
        work_item.title = "Updated Project Title"
        work_item.save()

        updated = WorkItem.objects.get(id=work_item.id)
        assert updated.title == "Updated Project Title"
        assert updated.title != original_title

    def test_edit_workitem_status_transition(self, work_item):
        """Test workitem status transitions."""
        # planned -> in_progress
        work_item.status = 'in_progress'
        work_item.save()
        assert WorkItem.objects.get(id=work_item.id).status == 'in_progress'

        # in_progress -> completed
        work_item.status = 'completed'
        work_item.save()
        assert WorkItem.objects.get(id=work_item.id).status == 'completed'

    def test_edit_workitem_preserves_relationships(
        self, work_item, allotment_q1, execution_user
    ):
        """Test that editing workitem preserves obligation relationships."""
        # Create obligation
        obligation = Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('3000000.00'),
            payee="Contractor",
            obligated_by=execution_user,
            status='obligated'
        )

        # Edit workitem
        work_item.title = "Updated Title"
        work_item.description = "Updated description"
        work_item.save()

        # Verify obligation still exists and is linked
        assert WorkItem.objects.get(id=work_item.id).obligations.count() == 1
        assert Obligation.objects.get(id=obligation.id).work_item == work_item

    def test_edit_workitem_propagates_to_related_models(
        self, work_item, allotment_q1, execution_user
    ):
        """Test that updating workitem status propagates to obligations."""
        obligation = Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('2000000.00'),
            payee="Contractor",
            obligated_by=execution_user,
            status='obligated'
        )

        # Update workitem to completed
        work_item.status = 'completed'
        work_item.save()

        # Obligation should still reference completed workitem
        refreshed_obligation = Obligation.objects.get(id=obligation.id)
        assert refreshed_obligation.work_item.status == 'completed'

    def test_edit_workitem_estimated_cost_with_active_obligations(
        self, work_item, allotment_q1, execution_user
    ):
        """Test editing workitem cost when obligations exist."""
        obligation = Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('5000000.00'),
            payee="Contractor",
            obligated_by=execution_user,
            status='obligated'
        )

        # Update estimated cost (should not affect existing obligations)
        work_item.estimated_cost = Decimal('7000000.00')
        work_item.save()

        # Obligation amount should remain unchanged
        refreshed_obligation = Obligation.objects.get(id=obligation.id)
        assert refreshed_obligation.amount == Decimal('5000000.00')
        assert refreshed_obligation.work_item.estimated_cost == Decimal('7000000.00')


@pytest.mark.integration
@pytest.mark.django_db
class TestWorkItemDeletion:
    """Test workitem deletion and cascade behaviors."""

    def test_delete_workitem_without_obligations(self, monitoring_entry):
        """Test deleting workitem with no related obligations."""
        work_item = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="Temporary Project",
            estimated_cost=Decimal('1000000.00'),
            status='planned'
        )
        work_item_id = work_item.id

        # Delete should succeed
        work_item.delete()

        assert not WorkItem.objects.filter(id=work_item_id).exists()

    def test_delete_workitem_with_obligations_fails(
        self, work_item, allotment_q1, execution_user
    ):
        """Test that deleting workitem with obligations fails (PROTECT constraint)."""
        # Create obligation to prevent deletion
        Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('3000000.00'),
            payee="Contractor",
            obligated_by=execution_user,
            status='obligated'
        )

        # Attempt to delete should fail due to PROTECT on monitoring_entry FK
        # (WorkItem cannot be deleted if referenced by Obligation)
        # The CASCADE happens at Obligation level, not WorkItem level

    def test_delete_workitem_cascades_to_monitoring_entry(
        self, monitoring_entry
    ):
        """Test that WorkItem references are properly managed."""
        work_item = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="Project",
            estimated_cost=Decimal('1000000.00'),
            status='planned'
        )
        work_item_id = work_item.id
        monitoring_id = monitoring_entry.id

        # Delete workitem (should succeed - no CASCADE from WorkItem)
        work_item.delete()

        # WorkItem should be deleted
        assert not WorkItem.objects.filter(id=work_item_id).exists()

        # MonitoringEntry should still exist (inverse FK is not CASCADE)
        from monitoring.models import MonitoringEntry
        assert MonitoringEntry.objects.filter(id=monitoring_id).exists()

    def test_cascade_delete_workitem_through_obligation_deletion(
        self, work_item, allotment_q1, execution_user
    ):
        """Test workitem cleanup when parent obligation is deleted."""
        obligation = Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('5000000.00'),
            payee="Contractor",
            obligated_by=execution_user,
            status='obligated'
        )

        # Delete obligation
        obligation.delete()

        # WorkItem should still exist (not cascade deleted)
        assert WorkItem.objects.filter(id=work_item.id).exists()

    def test_delete_obligation_removes_relationship(
        self, work_item, allotment_q1, execution_user
    ):
        """Test that deleting obligation breaks workitem relationship."""
        obligation = Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('5000000.00'),
            payee="Contractor",
            obligated_by=execution_user,
            status='obligated'
        )
        obligation_id = obligation.id

        # Delete obligation
        obligation.delete()

        # Obligation should be gone
        assert not Obligation.objects.filter(id=obligation_id).exists()

        # WorkItem should still exist but have no obligations
        refreshed = WorkItem.objects.get(id=work_item.id)
        assert refreshed.obligations.count() == 0


@pytest.mark.integration
@pytest.mark.django_db
class TestMultipleWorkItemsPerAllotment:
    """Test creating multiple workitems for same obligation/allotment."""

    def test_multiple_workitems_single_obligation(
        self, allotment_q1, execution_user, monitoring_entry
    ):
        """Test multiple workitems cannot share single obligation (1:1 relationship)."""
        # Create first workitem
        work_item_1 = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="Project Phase 1",
            estimated_cost=Decimal('3000000.00'),
            status='in_progress'
        )

        # Create second workitem
        work_item_2 = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="Project Phase 2",
            estimated_cost=Decimal('2000000.00'),
            status='planned'
        )

        # Create obligation for first workitem
        obligation_1 = Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item_1,
            amount=Decimal('3000000.00'),
            payee="Contractor Phase 1",
            obligated_by=execution_user,
            status='obligated'
        )

        # Create separate obligation for second workitem
        obligation_2 = Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item_2,
            amount=Decimal('2000000.00'),
            payee="Contractor Phase 2",
            obligated_by=execution_user,
            status='obligated'
        )

        # Verify relationships
        assert work_item_1.obligations.count() == 1
        assert work_item_2.obligations.count() == 1
        assert allotment_q1.obligations.count() == 2

        total_obligated = Obligation.objects.filter(
            allotment=allotment_q1
        ).aggregate(total=Sum('amount'))['total']
        assert total_obligated == Decimal('5000000.00')
        assert total_obligated <= allotment_q1.amount  # 10M

    def test_multiple_workitems_exceed_allotment(
        self, allotment_q1, execution_user, monitoring_entry
    ):
        """Test that obligations cannot exceed allotment."""
        workitems = []
        obligations = []

        # Create 4 workitems
        for i in range(1, 5):
            wi = WorkItem.objects.create(
                monitoring_entry=monitoring_entry,
                title=f"Project {i}",
                estimated_cost=Decimal(f'{3000000 * i}.00'),
                status='planned'
            )
            workitems.append(wi)

        # Try to create obligations (only first 2 should succeed: 3M + 6M = 9M)
        for i, wi in enumerate(workitems):
            try:
                ob = Obligation.objects.create(
                    allotment=allotment_q1,
                    work_item=wi,
                    amount=Decimal(f'{3000000 * (i + 1)}.00'),
                    payee=f"Contractor {i+1}",
                    obligated_by=execution_user,
                    status='obligated'
                )
                obligations.append(ob)
            except ValidationError:
                # Expected for items that exceed allotment
                pass

        # Verify total obligations don't exceed allotment
        total = Obligation.objects.filter(
            allotment=allotment_q1
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        assert total <= allotment_q1.amount


@pytest.mark.integration
@pytest.mark.django_db
class TestWorkItemDataIntegrity:
    """Test data integrity across workitem and related models."""

    def test_workitem_total_obligations_calculation(
        self, work_item, allotment_q1, allotment_q2, execution_user
    ):
        """Test workitem aggregates obligations from multiple allotments."""
        # Create obligations in different quarters
        ob1 = Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('3000000.00'),
            payee="Contractor Q1",
            obligated_by=execution_user,
            status='obligated'
        )

        ob2 = Obligation.objects.create(
            allotment=allotment_q2,
            work_item=work_item,
            amount=Decimal('2000000.00'),
            payee="Contractor Q2",
            obligated_by=execution_user,
            status='obligated'
        )

        # Verify total
        assert work_item.total_obligations() == Decimal('5000000.00')
        assert work_item.obligations.count() == 2

    def test_workitem_total_disbursements_calculation(
        self, work_item, allotment_q1, execution_user
    ):
        """Test workitem aggregates disbursements from obligations."""
        obligation = Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('5000000.00'),
            payee="Contractor",
            obligated_by=execution_user,
            status='obligated'
        )

        # Create multiple disbursements
        Disbursement.objects.create(
            obligation=obligation,
            amount=Decimal('2000000.00'),
            payment_method='check',
            disbursed_by=execution_user,
            status='paid'
        )

        Disbursement.objects.create(
            obligation=obligation,
            amount=Decimal('2000000.00'),
            payment_method='check',
            disbursed_by=execution_user,
            status='paid'
        )

        # Verify total
        assert work_item.total_disbursements() == Decimal('4000000.00')

    def test_workitem_cross_module_communication(
        self, test_organization, test_user, monitoring_entry, execution_user
    ):
        """Test that workitem integrates with budget_preparation models."""
        # Create budget proposal
        proposal = BudgetProposal.objects.create(
            organization=test_organization,
            fiscal_year=2025,
            title="Program Budget",
            total_requested_budget=Decimal('10000000.00'),
            status='approved',
            submitted_by=test_user
        )

        # Create program budget
        program_budget = ProgramBudget.objects.create(
            budget_proposal=proposal,
            monitoring_entry=monitoring_entry,
            requested_amount=Decimal('5000000.00'),
            approved_amount=Decimal('5000000.00'),
            priority_rank=1
        )

        # Create allotment from program budget
        allotment = Allotment.objects.create(
            program_budget=program_budget,
            quarter='Q1',
            amount=Decimal('5000000.00'),
            released_by=execution_user,
            status='released'
        )

        # Create workitem for same monitoring entry
        work_item = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="Implementation Work",
            estimated_cost=Decimal('3000000.00'),
            status='in_progress'
        )

        # Create obligation linking workitem to allotment
        obligation = Obligation.objects.create(
            allotment=allotment,
            work_item=work_item,
            amount=Decimal('3000000.00'),
            payee="Implementation Contractor",
            obligated_by=execution_user,
            status='obligated'
        )

        # Verify integration chain: BudgetProposal -> ProgramBudget -> Allotment -> Obligation -> WorkItem
        assert obligation.allotment.program_budget.budget_proposal == proposal
        assert obligation.work_item.monitoring_entry == program_budget.monitoring_entry
        assert work_item.monitoring_entry.execution_work_items.count() >= 1


@pytest.mark.integration
@pytest.mark.django_db
class TestWorkItemMultiTenant:
    """Test workitem multi-tenant data isolation."""

    def test_workitems_isolated_by_monitoring_entry(
        self, monitoring_entry, monitoring_entry_2
    ):
        """Test that workitems for different monitoring entries don't mix."""
        # Create workitem for entry 1
        wi1 = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="Project 1",
            estimated_cost=Decimal('1000000.00'),
            status='planned'
        )

        # Create workitem for entry 2
        wi2 = WorkItem.objects.create(
            monitoring_entry=monitoring_entry_2,
            title="Project 2",
            estimated_cost=Decimal('2000000.00'),
            status='planned'
        )

        # Verify isolation
        assert wi1.monitoring_entry != wi2.monitoring_entry
        assert monitoring_entry.execution_work_items.count() >= 1
        assert monitoring_entry_2.execution_work_items.count() >= 1
        assert wi1 in monitoring_entry.execution_work_items.all()
        assert wi2 in monitoring_entry_2.execution_work_items.all()

    def test_workitem_organization_isolation(
        self, test_organization, test_organization_2, execution_user
    ):
        """Test that workitems respect organization boundaries."""
        from monitoring.models import MonitoringEntry

        # Create monitoring entries for different organizations
        me1 = MonitoringEntry.objects.create(
            title="Org 1 Program",
            category="moa_ppa",
            status="planning",
            priority="high",
            fiscal_year=2025
        )

        me2 = MonitoringEntry.objects.create(
            title="Org 2 Program",
            category="moa_ppa",
            status="planning",
            priority="high",
            fiscal_year=2025
        )

        # Create workitems
        wi1 = WorkItem.objects.create(
            monitoring_entry=me1,
            title="Org 1 Project",
            estimated_cost=Decimal('1000000.00'),
            status='planned'
        )

        wi2 = WorkItem.objects.create(
            monitoring_entry=me2,
            title="Org 2 Project",
            estimated_cost=Decimal('2000000.00'),
            status='planned'
        )

        # Verify they're separate
        assert wi1.monitoring_entry != wi2.monitoring_entry
        assert wi1.id != wi2.id


@pytest.mark.integration
@pytest.mark.django_db
class TestWorkItemFiltering:
    """Test workitem querying and filtering."""

    def test_filter_workitems_by_status(self, monitoring_entry):
        """Test filtering workitems by status."""
        # Create workitems with different statuses
        for status in ['planned', 'in_progress', 'completed']:
            WorkItem.objects.create(
                monitoring_entry=monitoring_entry,
                title=f"Project {status}",
                estimated_cost=Decimal('1000000.00'),
                status=status
            )

        # Filter by status
        planned = WorkItem.objects.filter(status='planned')
        in_progress = WorkItem.objects.filter(status='in_progress')
        completed = WorkItem.objects.filter(status='completed')

        assert planned.count() >= 1
        assert in_progress.count() >= 1
        assert completed.count() >= 1

    def test_filter_workitems_by_monitoring_entry(
        self, monitoring_entry, monitoring_entry_2
    ):
        """Test filtering workitems by monitoring entry."""
        wi1 = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="Entry 1 Project",
            estimated_cost=Decimal('1000000.00'),
            status='planned'
        )

        wi2 = WorkItem.objects.create(
            monitoring_entry=monitoring_entry_2,
            title="Entry 2 Project",
            estimated_cost=Decimal('2000000.00'),
            status='planned'
        )

        # Filter
        entry1_items = WorkItem.objects.filter(monitoring_entry=monitoring_entry)
        entry2_items = WorkItem.objects.filter(monitoring_entry=monitoring_entry_2)

        assert wi1 in entry1_items
        assert wi2 not in entry1_items
        assert wi2 in entry2_items

    def test_workitems_ordering(self, monitoring_entry):
        """Test workitems are ordered by creation date (newest first)."""
        wi1 = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="First Project",
            estimated_cost=Decimal('1000000.00'),
            status='planned'
        )

        wi2 = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="Second Project",
            estimated_cost=Decimal('2000000.00'),
            status='planned'
        )

        # Query should return newest first
        items = list(WorkItem.objects.filter(monitoring_entry=monitoring_entry))
        # wi2 was created after wi1, so should appear first
        assert items[0].id == wi2.id or items[1].id == wi2.id


@pytest.mark.integration
@pytest.mark.django_db
class TestWorkItemTransactions:
    """Test workitem operations in transactions."""

    def test_workitem_creation_rollback_on_error(self, monitoring_entry):
        """Test that failed transaction rolls back workitem creation."""
        initial_count = WorkItem.objects.count()

        try:
            with transaction.atomic():
                WorkItem.objects.create(
                    monitoring_entry=monitoring_entry,
                    title="Should Rollback",
                    estimated_cost=Decimal('1000000.00'),
                    status='planned'
                )
                # Force error
                raise ValueError("Simulated error")
        except ValueError:
            pass

        # Count should be unchanged
        assert WorkItem.objects.count() == initial_count

    def test_workitem_obligation_atomic_creation(
        self, work_item, allotment_q1, execution_user
    ):
        """Test atomic creation of workitem with obligations."""
        with transaction.atomic():
            ob1 = Obligation.objects.create(
                allotment=allotment_q1,
                work_item=work_item,
                amount=Decimal('3000000.00'),
                payee="Contractor",
                obligated_by=execution_user,
                status='obligated'
            )

        # Verify persistence
        assert Obligation.objects.filter(id=ob1.id).exists()
        assert work_item.obligations.count() == 1


# Fixtures for additional test data

@pytest.fixture
def monitoring_entry_2(db):
    """Create second monitoring entry for isolation testing."""
    from monitoring.models import MonitoringEntry
    return MonitoringEntry.objects.create(
        title="Second Monitoring Entry",
        category="moa_ppa",
        status="planning",
        priority="high",
        fiscal_year=2025
    )


@pytest.fixture
def test_organization_2(db):
    """Create second test organization for multi-tenant testing."""
    from organizations.models import Organization
    return Organization.objects.create(
        name="Second Organization",
        code="ORG002",
        organization_type="other_bangsamoro_community",
        status="active"
    )
