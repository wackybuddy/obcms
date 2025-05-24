from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import User, Region, Province, Municipality, Barangay
from .forms import UserRegistrationForm, CustomLoginForm

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the custom User model."""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'oobc_staff',
            'organization': 'OOBC Test',
            'position': 'Test Position',
            'contact_number': '+639123456789',
        }
    
    def test_create_user(self):
        """Test creating a new user."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.user_type, 'oobc_staff')
        self.assertFalse(user.is_approved)  # Should be False by default
        self.assertTrue(user.is_active)
    
    def test_user_str_method(self):
        """Test the __str__ method of User."""
        user = User.objects.create_user(**self.user_data)
        expected = "Test User (OOBC Staff)"
        self.assertEqual(str(user), expected)
    
    def test_user_properties(self):
        """Test user property methods."""
        user = User.objects.create_user(**self.user_data)
        
        # Test is_oobc_staff property
        self.assertTrue(user.is_oobc_staff)
        
        # Test is_community_leader property
        user.user_type = 'community_leader'
        user.save()
        self.assertTrue(user.is_community_leader)
        
        # Test can_approve_users property
        user.user_type = 'admin'
        user.is_superuser = True
        user.save()
        self.assertTrue(user.can_approve_users)
    
    def test_user_approval_workflow(self):
        """Test user approval workflow."""
        # Create admin user
        admin_user = User.objects.create_user(
            username='admin',
            user_type='admin',
            is_superuser=True
        )
        
        # Create regular user
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_approved)
        self.assertIsNone(user.approved_by)
        self.assertIsNone(user.approved_at)
        
        # Approve user
        user.is_approved = True
        user.approved_by = admin_user
        user.approved_at = timezone.now()
        user.save()
        
        self.assertTrue(user.is_approved)
        self.assertEqual(user.approved_by, admin_user)
        self.assertIsNotNone(user.approved_at)


class UserRegistrationFormTest(TestCase):
    """Test cases for UserRegistrationForm."""
    
    def setUp(self):
        self.form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'user_type': 'lgu',
            'organization': 'Test LGU',
            'position': 'Mayor',
            'contact_number': '+639987654321',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!',
        }
    
    def test_valid_registration_form(self):
        """Test valid registration form."""
        form = UserRegistrationForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        """Test password mismatch validation."""
        self.form_data['password2'] = 'DifferentPassword123!'
        form = UserRegistrationForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_duplicate_email(self):
        """Test duplicate email validation."""
        # Create existing user
        User.objects.create_user(
            username='existing',
            email='newuser@example.com'
        )
        
        form = UserRegistrationForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_save(self):
        """Test form save method."""
        form = UserRegistrationForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.user_type, 'lgu')
        self.assertFalse(user.is_approved)  # Should be False for new registrations


class CustomLoginFormTest(TestCase):
    """Test cases for CustomLoginForm."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            user_type='oobc_staff',
            is_approved=True
        )
    
    def test_login_with_username(self):
        """Test login with username."""
        form_data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        form = CustomLoginForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_login_with_email(self):
        """Test login with email."""
        form_data = {
            'username': 'test@example.com',  # Using email as username
            'password': 'TestPassword123!'
        }
        form = CustomLoginForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials."""
        form_data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        form = CustomLoginForm(data=form_data)
        self.assertFalse(form.is_valid())


class AuthenticationViewsTest(TestCase):
    """Test cases for authentication views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            user_type='oobc_staff',
            is_approved=True
        )
        self.unapproved_user = User.objects.create_user(
            username='unapproved',
            email='unapproved@example.com',
            password='TestPassword123!',
            user_type='lgu',
            is_approved=False
        )
    
    def test_login_view_get(self):
        """Test GET request to login view."""
        response = self.client.get(reverse('common:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in to your account')
    
    def test_login_view_post_success(self):
        """Test successful login."""
        response = self.client.post(reverse('common:login'), {
            'username': 'testuser',
            'password': 'TestPassword123!'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
    
    def test_login_view_post_unapproved_user(self):
        """Test login attempt with unapproved user."""
        response = self.client.post(reverse('common:login'), {
            'username': 'unapproved',
            'password': 'TestPassword123!'
        })
        self.assertEqual(response.status_code, 200)  # Should not redirect
        self.assertContains(response, 'pending approval')
    
    def test_registration_view_get(self):
        """Test GET request to registration view."""
        response = self.client.get(reverse('common:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create your account')
    
    def test_registration_view_post(self):
        """Test POST request to registration view."""
        response = self.client.post(reverse('common:register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'user_type': 'nga',
            'organization': 'Test Agency',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        
        # Check if user was created
        new_user = User.objects.get(username='newuser')
        self.assertFalse(new_user.is_approved)  # Should be unapproved
    
    def test_dashboard_view_authenticated(self):
        """Test dashboard view for authenticated user."""
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.get(reverse('common:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'testuser')
    
    def test_dashboard_view_unauthenticated(self):
        """Test dashboard view for unauthenticated user."""
        response = self.client.get(reverse('common:dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
    
    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user."""
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.get(reverse('common:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User Profile')
        self.assertContains(response, 'testuser')
    
    def test_logout_view(self):
        """Test logout functionality."""
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.post(reverse('common:logout'))
        self.assertEqual(response.status_code, 302)  # Should redirect after logout


class AdministrativeHierarchyModelTests(TestCase):
    """Test cases for administrative hierarchy models."""
    
    def setUp(self):
        """Set up test data."""
        self.region = Region.objects.create(
            code='IX',
            name='Zamboanga Peninsula',
            description='Region IX encompasses the Zamboanga Peninsula'
        )
        
        self.province = Province.objects.create(
            region=self.region,
            code='ZAM_DEL_SUR',
            name='Zamboanga del Sur',
            capital='Pagadian City'
        )
        
        self.municipality = Municipality.objects.create(
            province=self.province,
            code='ZAMBOANGA_CITY',
            name='Zamboanga',
            municipality_type='independent_city'
        )
        
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code='CAMPO_ISLAM',
            name='Campo Islam',
            is_urban=True
        )
    
    def test_region_creation(self):
        """Test region model creation and properties."""
        self.assertEqual(self.region.code, 'IX')
        self.assertEqual(self.region.name, 'Zamboanga Peninsula')
        self.assertTrue(self.region.is_active)
        self.assertIsNotNone(self.region.created_at)
        
        # Test string representation
        expected_str = "Region IX - Zamboanga Peninsula"
        self.assertEqual(str(self.region), expected_str)
    
    def test_region_province_count(self):
        """Test region province count property."""
        # Initially should have 1 province
        self.assertEqual(self.region.province_count, 1)
        
        # Add another province
        Province.objects.create(
            region=self.region,
            code='ZAM_DEL_NORTE',
            name='Zamboanga del Norte'
        )
        self.assertEqual(self.region.province_count, 2)
        
        # Inactive province should not count
        Province.objects.create(
            region=self.region,
            code='ZAM_SIBUGAY',
            name='Zamboanga Sibugay',
            is_active=False
        )
        self.assertEqual(self.region.province_count, 2)
    
    def test_province_creation(self):
        """Test province model creation and properties."""
        self.assertEqual(self.province.code, 'ZAM_DEL_SUR')
        self.assertEqual(self.province.name, 'Zamboanga del Sur')
        self.assertEqual(self.province.capital, 'Pagadian City')
        self.assertEqual(self.province.region, self.region)
        
        # Test string representation
        expected_str = "Zamboanga del Sur, Zamboanga Peninsula"
        self.assertEqual(str(self.province), expected_str)
        
        # Test full path
        expected_path = "Region IX > Zamboanga del Sur"
        self.assertEqual(self.province.full_path, expected_path)
    
    def test_province_municipality_count(self):
        """Test province municipality count property."""
        # Initially should have 1 municipality
        self.assertEqual(self.province.municipality_count, 1)
        
        # Add another municipality
        Municipality.objects.create(
            province=self.province,
            code='PAGADIAN',
            name='Pagadian',
            municipality_type='city'
        )
        self.assertEqual(self.province.municipality_count, 2)
    
    def test_municipality_creation(self):
        """Test municipality model creation and properties."""
        self.assertEqual(self.municipality.code, 'ZAMBOANGA_CITY')
        self.assertEqual(self.municipality.name, 'Zamboanga')
        self.assertEqual(self.municipality.municipality_type, 'independent_city')
        self.assertEqual(self.municipality.province, self.province)
        
        # Test string representation
        expected_str = "Independent City of Zamboanga, Zamboanga del Sur"
        self.assertEqual(str(self.municipality), expected_str)
        
        # Test full path
        expected_path = "Region IX > Zamboanga del Sur > Zamboanga"
        self.assertEqual(self.municipality.full_path, expected_path)
    
    def test_municipality_barangay_count(self):
        """Test municipality barangay count property."""
        # Initially should have 1 barangay
        self.assertEqual(self.municipality.barangay_count, 1)
        
        # Add another barangay
        Barangay.objects.create(
            municipality=self.municipality,
            code='RIO_HONDO',
            name='Rio Hondo',
            is_urban=True
        )
        self.assertEqual(self.municipality.barangay_count, 2)
    
    def test_barangay_creation(self):
        """Test barangay model creation and properties."""
        self.assertEqual(self.barangay.code, 'CAMPO_ISLAM')
        self.assertEqual(self.barangay.name, 'Campo Islam')
        self.assertTrue(self.barangay.is_urban)
        self.assertEqual(self.barangay.municipality, self.municipality)
        
        # Test string representation
        expected_str = "Barangay Campo Islam, Zamboanga"
        self.assertEqual(str(self.barangay), expected_str)
        
        # Test full path
        expected_path = ("Region IX > Zamboanga del Sur > Zamboanga > "
                        "Barangay Campo Islam")
        self.assertEqual(self.barangay.full_path, expected_path)
    
    def test_barangay_properties(self):
        """Test barangay convenience properties."""
        # Test region property
        self.assertEqual(self.barangay.region, self.region)
        
        # Test province property
        self.assertEqual(self.barangay.province, self.province)
    
    def test_model_ordering(self):
        """Test model default ordering."""
        # Create additional regions
        region_xii = Region.objects.create(code='XII', name='SOCCSKSARGEN')
        region_x = Region.objects.create(code='X', name='Northern Mindanao')
        
        regions = list(Region.objects.all())
        self.assertEqual(regions[0].code, 'IX')
        self.assertEqual(regions[1].code, 'X')
        self.assertEqual(regions[2].code, 'XII')
    
    def test_unique_constraints(self):
        """Test unique constraints on codes."""
        # Test region code uniqueness
        with self.assertRaises(Exception):
            Region.objects.create(code='IX', name='Duplicate Region')
        
        # Test province code uniqueness
        with self.assertRaises(Exception):
            Province.objects.create(
                region=self.region,
                code='ZAM_DEL_SUR',
                name='Duplicate Province'
            )
        
        # Test municipality code uniqueness
        with self.assertRaises(Exception):
            Municipality.objects.create(
                province=self.province,
                code='ZAMBOANGA_CITY',
                name='Duplicate Municipality'
            )
        
        # Test barangay code uniqueness
        with self.assertRaises(Exception):
            Barangay.objects.create(
                municipality=self.municipality,
                code='CAMPO_ISLAM',
                name='Duplicate Barangay'
            )
    
    def test_cascade_relationships(self):
        """Test cascade delete relationships."""
        # Count initial objects
        initial_provinces = Province.objects.count()
        initial_municipalities = Municipality.objects.count()
        initial_barangays = Barangay.objects.count()
        
        # Delete region should cascade to all related objects
        self.region.delete()
        
        # Verify cascade deletion
        self.assertEqual(Province.objects.count(), initial_provinces - 1)
        self.assertEqual(Municipality.objects.count(), initial_municipalities - 1)
        self.assertEqual(Barangay.objects.count(), initial_barangays - 1)
