from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from .models import OBCCommunity, Stakeholder, StakeholderEngagement
from common.models import Region, Province, Municipality, Barangay

User = get_user_model()


class StakeholderModelTest(TestCase):
    """Test cases for Stakeholder model."""
    
    def setUp(self):
        """Set up test data."""
        # Create geographic hierarchy
        self.region = Region.objects.create(
            code='IX', name='Zamboanga Peninsula'
        )
        self.province = Province.objects.create(
            code='0971', name='Zamboanga del Sur', region=self.region
        )
        self.municipality = Municipality.objects.create(
            code='097101', name='Zamboanga City', province=self.province
        )
        self.barangay = Barangay.objects.create(
            code='09710101', name='Arena Blanco', municipality=self.municipality
        )
        
        # Create test community
        self.community = OBCCommunity.objects.create(
            name='Test Community',
            barangay=self.barangay,
            population=500,
            households=100,
            development_status='developing'
        )
    
    def test_stakeholder_creation(self):
        """Test stakeholder creation with all required fields."""
        stakeholder = Stakeholder.objects.create(
            full_name='Abdullah Bin Jamil',
            nickname='Haji Abdullah',
            stakeholder_type='community_leader',
            community=self.community,
            position='Pangkuluman',
            contact_number='+63917-555-0101',
            influence_level='high',
            engagement_level='active',
            is_verified=True
        )
        
        self.assertEqual(stakeholder.full_name, 'Abdullah Bin Jamil')
        self.assertEqual(stakeholder.display_name, 'Haji Abdullah')
        self.assertEqual(stakeholder.community, self.community)
        self.assertTrue(stakeholder.is_verified)
        self.assertEqual(str(stakeholder), 'Haji Abdullah (Community Leader) - Test Community')
    
    def test_stakeholder_display_name_fallback(self):
        """Test that display_name falls back to full_name when nickname is empty."""
        stakeholder = Stakeholder.objects.create(
            full_name='Muhammad Hassan',
            stakeholder_type='imam',
            community=self.community
        )
        
        self.assertEqual(stakeholder.display_name, 'Muhammad Hassan')
    
    def test_stakeholder_years_of_service(self):
        """Test years_of_service calculation."""
        current_year = date.today().year
        stakeholder = Stakeholder.objects.create(
            full_name='Test Leader',
            stakeholder_type='community_leader',
            community=self.community,
            since_year=current_year - 5
        )
        
        self.assertEqual(stakeholder.years_of_service, 5)
    
    def test_stakeholder_contact_info(self):
        """Test contact_info property formatting."""
        stakeholder = Stakeholder.objects.create(
            full_name='Test Leader',
            stakeholder_type='community_leader',
            community=self.community,
            contact_number='+63917-555-0101',
            email='test@example.com'
        )
        
        expected = 'Mobile: +63917-555-0101 | Email: test@example.com'
        self.assertEqual(stakeholder.contact_info, expected)
    
    def test_stakeholder_unique_constraint(self):
        """Test unique constraint on full_name, community, stakeholder_type."""
        # Create first stakeholder
        Stakeholder.objects.create(
            full_name='Abdullah Jamil',
            stakeholder_type='community_leader',
            community=self.community
        )
        
        # Try to create duplicate - should raise IntegrityError
        with self.assertRaises(Exception):
            Stakeholder.objects.create(
                full_name='Abdullah Jamil',
                stakeholder_type='community_leader',
                community=self.community
            )


class StakeholderEngagementModelTest(TestCase):
    """Test cases for StakeholderEngagement model."""
    
    def setUp(self):
        """Set up test data."""
        # Create geographic hierarchy
        self.region = Region.objects.create(
            code='IX', name='Zamboanga Peninsula'
        )
        self.province = Province.objects.create(
            code='0971', name='Zamboanga del Sur', region=self.region
        )
        self.municipality = Municipality.objects.create(
            code='097101', name='Zamboanga City', province=self.province
        )
        self.barangay = Barangay.objects.create(
            code='09710101', name='Arena Blanco', municipality=self.municipality
        )
        
        # Create test community and stakeholder
        self.community = OBCCommunity.objects.create(
            name='Test Community',
            barangay=self.barangay
        )
        self.stakeholder = Stakeholder.objects.create(
            full_name='Test Leader',
            stakeholder_type='community_leader',
            community=self.community
        )
    
    def test_engagement_creation(self):
        """Test stakeholder engagement creation."""
        engagement = StakeholderEngagement.objects.create(
            stakeholder=self.stakeholder,
            engagement_type='meeting',
            title='Monthly Community Meeting',
            description='Regular monthly meeting',
            date=date.today(),
            outcome='positive',
            documented_by='Field Officer'
        )
        
        self.assertEqual(engagement.stakeholder, self.stakeholder)
        self.assertEqual(engagement.engagement_type, 'meeting')
        self.assertEqual(engagement.outcome, 'positive')
        expected_str = f'Monthly Community Meeting - Test Leader ({date.today()})'
        self.assertEqual(str(engagement), expected_str)
    
    def test_engagement_follow_up(self):
        """Test engagement follow-up functionality."""
        engagement = StakeholderEngagement.objects.create(
            stakeholder=self.stakeholder,
            engagement_type='consultation',
            title='Needs Assessment',
            description='Community needs consultation',
            date=date.today(),
            follow_up_needed=True,
            follow_up_date=date.today() + timedelta(days=7),
            documented_by='Assessor'
        )
        
        self.assertTrue(engagement.follow_up_needed)
        self.assertEqual(
            engagement.follow_up_date, 
            date.today() + timedelta(days=7)
        )


class StakeholderAPITest(APITestCase):
    """Test cases for Stakeholder API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='oobc_staff',
            is_approved=True
        )
        
        # Create geographic hierarchy
        self.region = Region.objects.create(
            code='IX', name='Zamboanga Peninsula'
        )
        self.province = Province.objects.create(
            code='0971', name='Zamboanga del Sur', region=self.region
        )
        self.municipality = Municipality.objects.create(
            code='097101', name='Zamboanga City', province=self.province
        )
        self.barangay = Barangay.objects.create(
            code='09710101', name='Arena Blanco', municipality=self.municipality
        )
        
        # Create test community
        self.community = OBCCommunity.objects.create(
            name='Test Community',
            barangay=self.barangay,
            population=500,
            households=100
        )
        
        # Create test stakeholder
        self.stakeholder = Stakeholder.objects.create(
            full_name='Abdullah Jamil',
            nickname='Haji Abdullah',
            stakeholder_type='community_leader',
            community=self.community,
            position='Community Leader',
            contact_number='+63917-555-0101',
            influence_level='high',
            engagement_level='active'
        )
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
    
    def test_stakeholder_list_api(self):
        """Test stakeholder list API endpoint."""
        url = reverse('communities_api:stakeholder-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Abdullah Jamil')
    
    def test_stakeholder_detail_api(self):
        """Test stakeholder detail API endpoint."""
        url = reverse('communities_api:stakeholder-detail', args=[self.stakeholder.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Abdullah Jamil')
        self.assertEqual(response.data['display_name'], 'Haji Abdullah')
        self.assertEqual(response.data['community_name'], 'Test Community')
    
    def test_stakeholder_create_api(self):
        """Test stakeholder creation via API."""
        url = reverse('communities_api:stakeholder-list')
        data = {
            'full_name': 'Muhammad Hassan',
            'stakeholder_type': 'imam',
            'community': self.community.id,
            'position': 'Imam',
            'influence_level': 'medium',
            'engagement_level': 'active'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Stakeholder.objects.count(), 2)
        self.assertEqual(response.data['full_name'], 'Muhammad Hassan')
    
    def test_stakeholder_update_api(self):
        """Test stakeholder update via API."""
        url = reverse('communities_api:stakeholder-detail', args=[self.stakeholder.id])
        data = {
            'full_name': 'Abdullah Jamil',
            'stakeholder_type': 'community_leader',
            'community': self.community.id,
            'position': 'Senior Community Leader',
            'influence_level': 'very_high',
            'engagement_level': 'very_active'
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.stakeholder.refresh_from_db()
        self.assertEqual(self.stakeholder.position, 'Senior Community Leader')
        self.assertEqual(self.stakeholder.influence_level, 'very_high')
    
    def test_stakeholder_verify_api(self):
        """Test stakeholder verification via API."""
        url = reverse('communities_api:stakeholder-verify', args=[self.stakeholder.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.stakeholder.refresh_from_db()
        self.assertTrue(self.stakeholder.is_verified)
        self.assertIsNotNone(self.stakeholder.verification_date)
    
    def test_stakeholder_statistics_api(self):
        """Test stakeholder statistics API endpoint."""
        url = reverse('communities_api:stakeholder-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_stakeholders'], 1)
        self.assertEqual(response.data['active_stakeholders'], 1)
        self.assertIn('by_type', response.data)
        self.assertIn('by_influence_level', response.data)
    
    def test_stakeholder_filter_by_type(self):
        """Test stakeholder filtering by type."""
        # Create another stakeholder with different type
        Stakeholder.objects.create(
            full_name='Muhammad Hassan',
            stakeholder_type='imam',
            community=self.community
        )
        
        url = reverse('communities_api:stakeholder-list')
        response = self.client.get(url, {'stakeholder_type': 'community_leader'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['stakeholder_type'], 'community_leader')
    
    def test_stakeholder_search(self):
        """Test stakeholder search functionality."""
        url = reverse('communities_api:stakeholder-list')
        response = self.client.get(url, {'search': 'Abdullah'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Abdullah Jamil')


class StakeholderEngagementAPITest(APITestCase):
    """Test cases for StakeholderEngagement API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='oobc_staff',
            is_approved=True
        )
        
        # Create geographic hierarchy
        self.region = Region.objects.create(
            code='IX', name='Zamboanga Peninsula'
        )
        self.province = Province.objects.create(
            code='0971', name='Zamboanga del Sur', region=self.region
        )
        self.municipality = Municipality.objects.create(
            code='097101', name='Zamboanga City', province=self.province
        )
        self.barangay = Barangay.objects.create(
            code='09710101', name='Arena Blanco', municipality=self.municipality
        )
        
        # Create test community and stakeholder
        self.community = OBCCommunity.objects.create(
            name='Test Community',
            barangay=self.barangay
        )
        self.stakeholder = Stakeholder.objects.create(
            full_name='Test Leader',
            stakeholder_type='community_leader',
            community=self.community
        )
        
        # Create test engagement
        self.engagement = StakeholderEngagement.objects.create(
            stakeholder=self.stakeholder,
            engagement_type='meeting',
            title='Test Meeting',
            description='Test engagement',
            date=date.today(),
            documented_by='Test Officer'
        )
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
    
    def test_engagement_list_api(self):
        """Test engagement list API endpoint."""
        url = reverse('communities_api:stakeholderengagement-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Meeting')
    
    def test_engagement_create_api(self):
        """Test engagement creation via API."""
        url = reverse('communities_api:stakeholderengagement-list')
        data = {
            'stakeholder': self.stakeholder.id,
            'engagement_type': 'consultation',
            'title': 'New Consultation',
            'description': 'Test consultation engagement',
            'date': date.today().isoformat(),
            'outcome': 'positive',
            'documented_by': 'Field Officer'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StakeholderEngagement.objects.count(), 2)
        self.assertEqual(response.data['title'], 'New Consultation')
    
    def test_engagement_filter_by_stakeholder(self):
        """Test engagement filtering by stakeholder."""
        url = reverse('communities_api:stakeholderengagement-list')
        response = self.client.get(url, {'stakeholder': self.stakeholder.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['stakeholder'], self.stakeholder.id)
    
    def test_engagement_recent_endpoint(self):
        """Test recent engagements endpoint."""
        url = reverse('communities_api:stakeholderengagement-recent')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include today's engagement
        self.assertEqual(len(response.data), 1)


class StakeholderAdminTest(TestCase):
    """Test cases for Stakeholder admin functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create geographic hierarchy
        self.region = Region.objects.create(
            code='IX', name='Zamboanga Peninsula'
        )
        self.province = Province.objects.create(
            code='0971', name='Zamboanga del Sur', region=self.region
        )
        self.municipality = Municipality.objects.create(
            code='097101', name='Zamboanga City', province=self.province
        )
        self.barangay = Barangay.objects.create(
            code='09710101', name='Arena Blanco', municipality=self.municipality
        )
        
        # Create test community
        self.community = OBCCommunity.objects.create(
            name='Test Community',
            barangay=self.barangay
        )
        
        # Create test stakeholder
        self.stakeholder = Stakeholder.objects.create(
            full_name='Test Leader',
            stakeholder_type='community_leader',
            community=self.community
        )
        
        # Login admin user
        self.client.force_login(self.admin_user)
    
    def test_stakeholder_admin_list_view(self):
        """Test stakeholder admin list view."""
        url = '/admin/communities/stakeholder/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Leader')
    
    def test_stakeholder_admin_detail_view(self):
        """Test stakeholder admin detail view."""
        url = f'/admin/communities/stakeholder/{self.stakeholder.id}/change/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Leader')
        self.assertContains(response, 'community_leader')
    
    def test_stakeholder_admin_verification_action(self):
        """Test bulk verification action in admin."""
        url = '/admin/communities/stakeholder/'
        data = {
            'action': 'mark_as_verified',
            '_selected_action': [str(self.stakeholder.id)]
        }
        response = self.client.post(url, data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.stakeholder.refresh_from_db()
        self.assertTrue(self.stakeholder.is_verified)