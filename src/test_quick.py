"""Quick test to debug workitem integration tests."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.test')
django.setup()

from decimal import Decimal
from django.contrib.auth import get_user_model
from budget_execution.models import WorkItem
from monitoring.models import MonitoringEntry
from coordination.models import Organization as CoordinationOrganization
from organizations.models import Organization

User = get_user_model()

# Try to create monitoring entry
print("Creating test_organization...")
org, created = Organization.objects.get_or_create(
    code="OOBC",
    defaults={
        "name": "Office for Other Bangsamoro Communities",
        "acronym": "OOBC",
        "org_type": "office",
        "is_active": True,
    },
)
print(f"Organization created: {org}")

print("Creating coordination_org...")
coordination_org, created = CoordinationOrganization.objects.get_or_create(
    name=org.name,
    defaults={
        "acronym": org.acronym or org.code,
        "organization_type": "bmoa",
        "description": "Test coordination record for budget monitoring entry",
        "partnership_status": "active",
        "is_active": True,
    },
)
print(f"Coordination org created: {coordination_org}")

print("Creating monitoring_entry...")
me = MonitoringEntry.objects.create(
    title="Education Infrastructure Program",
    category="moa_ppa",
    summary="Build schools and learning centers",
    status="planning",
    priority="high",
    lead_organization=coordination_org,
    implementing_moa=coordination_org,
    fiscal_year=2025
)
print(f"Monitoring entry created: {me}")

print("Creating WorkItem...")
wi = WorkItem.objects.create(
    monitoring_entry=me,
    title="Test Project",
    description="Test",
    estimated_cost=Decimal('1000000.00'),
    status='planned'
)
print(f"WorkItem created: {wi}")
print(f"Total obligations: {wi.total_obligations()}")
print(f"Total disbursements: {wi.total_disbursements()}")
print("SUCCESS!")
