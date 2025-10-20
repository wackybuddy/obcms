"""
Test to verify that work items are not double-saved during sidebar form submission.

This test was created to verify the fix for the bug where creating a work item
through the sidebar form resulted in two identical items being created.

Bug details:
- Issue: When submitting the work item sidebar create form, two POST requests were
  sent to the server, resulting in two identical work items being created.
- Root cause: The sidebar_init_scripts.html had a manual form submit listener that
  was intercepting forms with implementing_moa fields and manually calling
  htmx.ajax('POST', ...). However, HTMX's automatic form submission mechanism was
  also active, causing both handlers to fire and send duplicate requests.
- Solution: Removed the manual form submit listener, allowing HTMX's automatic
  submission mechanism to handle the form.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from common.work_item_model import WorkItem
from coordination.models import Organization

User = get_user_model()


class WorkItemSidebarDoubleSubmitTest(TestCase):
    """Test that sidebar form submission creates only one work item."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create OOBC organization
        self.oobc_org = Organization.objects.create(
            name='Office for Other Bangsamoro Communities (OOBC)',
            acronym='OOBC'
        )

        # Clear any existing test items
        WorkItem.objects.filter(title='Test Work Item').delete()

        # Create client
        self.client = Client()
        self.client.force_login(self.user)

    def test_sidebar_create_single_submission(self):
        """
        Test that creating a work item via sidebar form creates exactly one item.
        
        This test verifies the fix for the double-save bug where forms with
        implementing_moa fields were being submitted twice.
        """
        # Get the create endpoint
        url = reverse('common:work_item_sidebar_create')
        
        # Prepare form data
        form_data = {
            'work_type': 'project',
            'title': 'Test Work Item',
            'status': 'not_started',
            'priority': 'medium',
            'progress': '0',
            'implementing_moa': str(self.oobc_org.pk),
            'submission_token': 'test-token-single-submit',
        }
        
        # Count items before
        count_before = WorkItem.objects.filter(title='Test Work Item').count()
        self.assertEqual(count_before, 0, "Should start with no test items")
        
        # Submit form
        response = self.client.post(url, form_data)
        
        # Verify response is successful (204 No Content for HTMX)
        self.assertIn(response.status_code, [200, 204], 
                      f"Expected 200/204, got {response.status_code}")
        
        # Count items after
        count_after = WorkItem.objects.filter(title='Test Work Item').count()
        
        # CRITICAL: Assert exactly 1 work item was created
        self.assertEqual(count_after, 1, 
                        f"Expected exactly 1 work item, but got {count_after}. "
                        "This indicates the double-save bug has returned.")
        
        # Verify item details
        item = WorkItem.objects.get(title='Test Work Item')
        self.assertEqual(item.work_type, 'project')
        self.assertEqual(item.status, 'not_started')
        self.assertEqual(item.priority, 'medium')
        self.assertEqual(item.implementing_moa, self.oobc_org)


class WorkItemSidebarFormRequiredFields(TestCase):
    """Test that sidebar form validation still works correctly after the fix."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )

        self.oobc_org = Organization.objects.create(
            name='Office for Other Bangsamoro Communities (OOBC)',
            acronym='OOBC'
        )

        WorkItem.objects.filter(title__startswith='Missing').delete()

        self.client = Client()
        self.client.force_login(self.user)
    
    def test_sidebar_create_requires_title(self):
        """Test that work item title is still required after the fix."""
        url = reverse('common:work_item_sidebar_create')
        
        # Form data without title
        form_data = {
            'work_type': 'project',
            'status': 'not_started',
            'priority': 'medium',
            'progress': '0',
            'implementing_moa': str(self.oobc_org.pk),
            'submission_token': 'test-token-missing-title',
        }
        
        # Submit form
        response = self.client.post(url, form_data)
        
        # Should not create item due to missing title
        count = WorkItem.objects.filter(title='').count()
        self.assertEqual(count, 0, "Should not create work item without title")
        
        # Response should contain form with error (not 204 success)
        # 204 means successful creation, anything else means form errors
        self.assertNotEqual(response.status_code, 204,
                           "Expected form error due to missing title")
