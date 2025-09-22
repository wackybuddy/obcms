"""Tests for coordination frontend views."""

from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from common.models import User

from ..models import (Organization, OrganizationContact, Partnership,
                     PartnershipSignatory)


class OrganizationCreateViewTests(TestCase):
    """Validate the frontend organization creation workflow."""

    def setUp(self):
        self.url = reverse("common:coordination_organization_add")
        self.user = User.objects.create_user(
            username="coordinator",
            password="secret123",
            email="coordinator@example.com",
            user_type="admin",
            is_approved=True,
        )

    def grant_permission(self):
        permission = Permission.objects.get(
            codename="add_organization",
            content_type__app_label="coordination",
        )
        self.user.user_permissions.add(permission)

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("common:login"), response.url)

    def test_permission_required(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_create_organization_with_contact(self):
        self.grant_permission()
        self.client.force_login(self.user)

        post_data = {
            "name": "Sample Org",
            "acronym": "SO",
            "organization_type": "ngo",
            "partnership_status": "active",
            "engagement_frequency": "as_needed",
            "address": "123 Main Street",
            "phone": "1234567",
            "email": "info@example.com",
            "contacts-TOTAL_FORMS": "1",
            "contacts-INITIAL_FORMS": "0",
            "contacts-MIN_NUM_FORMS": "0",
            "contacts-MAX_NUM_FORMS": "1000",
            "contacts-0-id": "",
            "contacts-0-contact_type": "primary",
            "contacts-0-first_name": "Jane",
            "contacts-0-last_name": "Doe",
            "contacts-0-middle_name": "",
            "contacts-0-title": "Ms",
            "contacts-0-position": "Coordinator",
            "contacts-0-department": "",
            "contacts-0-email": "jane@example.com",
            "contacts-0-phone": "1234567",
            "contacts-0-mobile": "",
            "contacts-0-alternative_email": "",
            "contacts-0-areas_of_responsibility": "Outreach",
            "contacts-0-languages_spoken": "English",
            "contacts-0-preferred_communication_method": "email",
            "contacts-0-best_contact_time": "Weekdays",
            "contacts-0-is_primary": "on",
            "contacts-0-is_active": "on",
            "contacts-0-notes": "Primary contact person",
        }

        response = self.client.post(self.url, post_data)

        self.assertRedirects(response, reverse("common:coordination_organizations"))
        organization = Organization.objects.get(name="Sample Org")
        self.assertEqual(organization.created_by, self.user)
        contact = OrganizationContact.objects.get(organization=organization)
        self.assertEqual(contact.first_name, "Jane")
        self.assertTrue(contact.is_primary)


class PartnershipCreateViewTests(TestCase):
    """Validate the frontend partnership creation workflow."""

    def setUp(self):
        self.url = reverse("common:coordination_partnership_add")
        self.user = User.objects.create_user(
            username="partner_admin",
            password="secret123",
            email="partner@example.com",
            user_type="admin",
            is_approved=True,
        )
        self.organization = Organization.objects.create(
            name="Alliance Org",
            organization_type="ngo",
            created_by=self.user,
        )

    def grant_permission(self):
        permission = Permission.objects.get(
            codename="add_partnership",
            content_type__app_label="coordination",
        )
        self.user.user_permissions.add(permission)

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("common:login"), response.url)

    def test_permission_required(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_create_partnership_with_signatory(self):
        self.grant_permission()
        self.client.force_login(self.user)

        post_data = {
            "title": "Strategic Collaboration",
            "partnership_type": "moa",
            "status": "active",
            "priority": "high",
            "progress_percentage": "10",
            "lead_organization": str(self.organization.pk),
            "organizations": [str(self.organization.pk)],
            "description": "Comprehensive partnership focusing on shared programs.",
            "objectives": "Advance community development initiatives collaboratively.",
            "scope": "Joint implementation across target areas.",
            "concept_date": "2024-01-01",
            "start_date": "2024-02-01",
            "end_date": "2024-12-31",
            "communication_plan": "Monthly coordination meetings.",
            "reporting_requirements": "Quarterly progress reports.",
            "is_renewable": "on",
            "renewal_criteria": "Subject to annual performance review.",
            "risks_identified": "Resource constraints.",
            "mitigation_strategies": "Allocate contingency budget.",
            "expected_outcomes": "Improved service delivery.",
            "actual_outcomes": "",
            "key_performance_indicators": "Number of beneficiaries reached.",
            "lessons_learned": "",
            "termination_clause": "Either party may terminate with notice.",
            "notes": "Initial rollout phase.",
            # Signatory formset
            "signatories-TOTAL_FORMS": "1",
            "signatories-INITIAL_FORMS": "0",
            "signatories-MIN_NUM_FORMS": "0",
            "signatories-MAX_NUM_FORMS": "1000",
            "signatories-0-id": "",
            "signatories-0-organization": str(self.organization.pk),
            "signatories-0-name": "Maria Santos",
            "signatories-0-position": "Executive Director",
            "signatories-0-signature_date": "2024-01-15",
            # Milestone formset (none)
            "milestones-TOTAL_FORMS": "0",
            "milestones-INITIAL_FORMS": "0",
            "milestones-MIN_NUM_FORMS": "0",
            "milestones-MAX_NUM_FORMS": "1000",
            # Document formset (none)
            "documents-TOTAL_FORMS": "0",
            "documents-INITIAL_FORMS": "0",
            "documents-MIN_NUM_FORMS": "0",
            "documents-MAX_NUM_FORMS": "1000",
        }

        response = self.client.post(self.url, post_data)

        self.assertRedirects(response, reverse("common:coordination_partnerships"))
        partnership = Partnership.objects.get(title="Strategic Collaboration")
        self.assertEqual(partnership.created_by, self.user)
        self.assertEqual(list(partnership.organizations.all()), [self.organization])
        signatory = PartnershipSignatory.objects.get(partnership=partnership)
        self.assertEqual(signatory.name, "Maria Santos")
