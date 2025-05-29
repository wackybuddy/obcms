from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User
from communities.models import OBCCommunity


class CustomLoginForm(AuthenticationForm):
    """Custom login form with OBC styling."""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def clean(self):
        """Custom authentication with approval check."""
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Try to find user by username or email
            try:
                if '@' in username:
                    user = User.objects.get(email=username)
                    username = user.username
                else:
                    user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid username or password.")
            
            # Authenticate the user
            self.user_cache = authenticate(
                self.request, 
                username=username, 
                password=password
            )
            
            if self.user_cache is None:
                raise forms.ValidationError("Invalid username or password.")
            
            # Check if user is active
            if not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")
        
        return self.cleaned_data


class UserRegistrationForm(UserCreationForm):
    """User registration form with OBC-specific fields."""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Enter your email address'
        })
    )
    user_type = forms.ChoiceField(
        choices=User.USER_TYPES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500'
        })
    )
    organization = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Organization or Agency Name (Optional)'
        })
    )
    position = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Position or Title (Optional)'
        })
    )
    contact_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': '+63 9XX XXX XXXX (Optional)'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 
                 'user_type', 'organization', 'position', 'contact_number', 
                 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes and placeholders to fields
        self.fields['username'].widget.attrs.update({
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Create a secure password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Confirm your password'
        })
    
    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        """Save the user with approval status set to False."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.user_type = self.cleaned_data['user_type']
        user.organization = self.cleaned_data['organization']
        user.position = self.cleaned_data['position']
        user.contact_number = self.cleaned_data['contact_number']
        user.is_approved = False  # Require approval for new users
        
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'organization', 
                 'position', 'contact_number')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        """Ensure email is unique (excluding current user)."""
        email = self.cleaned_data.get('email')
        if email:
            users_with_email = User.objects.filter(email=email)
            if self.instance:
                users_with_email = users_with_email.exclude(pk=self.instance.pk)
            if users_with_email.exists():
                raise forms.ValidationError("A user with this email already exists.")
        return email


class OBCCommunityForm(forms.ModelForm):
    """Comprehensive form for creating/editing OBC Communities."""
    
    class Meta:
        model = OBCCommunity
        fields = [
            # Identification & Location
            'obc_id', 'source_document_reference', 'community_names',
            'barangay', 'purok_sitio', 'specific_location', 'settlement_type',
            'latitude', 'longitude', 'proximity_to_barmm',
            
            # Demographics
            'estimated_obc_population', 'total_barangay_population',
            'households', 'families',
            'children_0_12', 'youth_13_30', 'adults_31_59', 'seniors_60_plus',
            'primary_ethnolinguistic_group', 'other_ethnolinguistic_groups',
            'languages_spoken',
            
            # Vulnerable Sectors
            'women_count', 'solo_parents_count', 'elderly_count',
            'pwd_count', 'farmers_count', 'fisherfolk_count',
            'indigenous_peoples_count', 'idps_count',
            'religious_leaders_ulama_count', 'csos_count', 'associations_count',
            'teachers_asatidz_count',
            
            # Socio-Economic Profile
            'primary_livelihoods', 'secondary_livelihoods',
            'estimated_poverty_incidence',
            'land_tenure_issues', 'number_of_employed_obc',
            'number_of_cooperatives', 'number_of_social_enterprises',
            'number_of_micro_enterprises', 'number_of_unbanked_obc',
            'financial_literacy_access',
            
            # Access to Basic Services
            'access_formal_education', 'access_als', 'access_madrasah',
            'access_healthcare', 'access_clean_water', 'access_sanitation',
            'access_electricity', 'access_roads_transport', 'access_communication',
            
            # Religious Facilities
            'has_mosque', 'has_madrasah', 'religious_leaders_count',
            
            # Development Status
            'development_status',
            
            # Contact Information (basic)
            'community_leader', 'leader_contact',
            
            # Administrative
            'is_active', 'notes'
        ]
        
        widgets = {
            # Text inputs
            'obc_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., R12-SK-PAL-001'}),
            'community_names': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Common name(s) used for the community'}),
            'purok_sitio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specific Purok/Sitio'}),
            'specific_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Additional location details'}),
            'languages_spoken': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Languages spoken (comma-separated)'}),
            'other_ethnolinguistic_groups': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Other groups (comma-separated)'}),
            'community_leader': forms.TextInput(attrs={'class': 'form-control'}),
            'leader_contact': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Number inputs
            'estimated_obc_population': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'total_barangay_population': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'households': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'families': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'children_0_12': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'youth_13_30': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'adults_31_59': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'seniors_60_plus': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'women_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'solo_parents_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'elderly_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'pwd_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'farmers_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'fisherfolk_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'indigenous_peoples_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'idps_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'religious_leaders_ulama_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'csos_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'associations_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'teachers_asatidz_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'religious_leaders_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'established_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1800', 'max': '2030'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            
            # Select inputs
            'barangay': forms.Select(attrs={'class': 'form-control'}),
            'settlement_type': forms.Select(attrs={'class': 'form-control'}),
            'proximity_to_barmm': forms.Select(attrs={'class': 'form-control'}),
            'primary_ethnolinguistic_group': forms.Select(attrs={'class': 'form-control'}),
            'estimated_poverty_incidence': forms.Select(attrs={'class': 'form-control'}),
            'development_status': forms.Select(attrs={'class': 'form-control'}),
            'relationship_with_lgu': forms.Select(attrs={'class': 'form-control'}),
            
            # Access rating selects
            'access_formal_education': forms.Select(attrs={'class': 'form-control'}),
            'access_als': forms.Select(attrs={'class': 'form-control'}),
            'access_madrasah': forms.Select(attrs={'class': 'form-control'}),
            'access_healthcare': forms.Select(attrs={'class': 'form-control'}),
            'access_clean_water': forms.Select(attrs={'class': 'form-control'}),
            'access_sanitation': forms.Select(attrs={'class': 'form-control'}),
            'access_electricity': forms.Select(attrs={'class': 'form-control'}),
            'access_roads_transport': forms.Select(attrs={'class': 'form-control'}),
            'access_communication': forms.Select(attrs={'class': 'form-control'}),
            
            # Textarea inputs
            'source_document_reference': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'primary_livelihoods': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'secondary_livelihoods': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'land_tenure_issues': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'number_of_employed_obc': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'number_of_cooperatives': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'number_of_social_enterprises': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'number_of_micro_enterprises': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'number_of_unbanked_obc': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'financial_literacy_access': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            
            # Checkbox inputs
            'has_mosque': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_madrasah': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        labels = {
            'obc_id': 'OBC ID',
            'source_document_reference': 'Source Document Reference',
            'community_names': 'Community Name(s)',
            'purok_sitio': 'Purok/Sitio',
            'specific_location': 'Specific Location',
            'settlement_type': 'Settlement Type',
            'proximity_to_barmm': 'Proximity to BARMM',
            'estimated_obc_population': 'Estimated OBC Population',
            'total_barangay_population': 'Total Barangay Population',
            'primary_ethnolinguistic_group': 'Primary Ethnolinguistic Group',
            'other_ethnolinguistic_groups': 'Other Ethnolinguistic Groups',
            'languages_spoken': 'Languages Spoken',
            'women_count': 'Number of Women',
            'solo_parents_count': 'Number of Solo Parents',
            'elderly_count': 'Number of Elderly',
            'pwd_count': 'Number of PWDs',
            'farmers_count': 'Number of Farmers',
            'fisherfolk_count': 'Number of Fisherfolk',
            'indigenous_peoples_count': 'Number of Indigenous Peoples',
            'idps_count': 'Number of IDPs',
            'religious_leaders_ulama_count': 'Number of Religious Leaders (Ulama)',
            'csos_count': 'Number of CSOs',
            'associations_count': 'Number of Associations',
            'teachers_asatidz_count': 'Number of Teachers/Asatidz',
            'estimated_poverty_incidence': 'Estimated Poverty Incidence',
            'number_of_employed_obc': 'Number of Employed OBC Individuals',
            'number_of_cooperatives': 'Number of Cooperatives',
            'number_of_social_enterprises': 'Number of Social Enterprises',
            'number_of_micro_enterprises': 'Number of Micro-Enterprises',
            'number_of_unbanked_obc': 'Number of Unbanked OBC Individuals',
            'access_formal_education': 'Access to Formal Education',
            'access_als': 'Access to ALS',
            'access_madrasah': 'Access to Madrasah',
            'access_healthcare': 'Access to Healthcare',
            'access_clean_water': 'Access to Clean Water',
            'access_sanitation': 'Access to Sanitation (Waste Management)',
            'access_electricity': 'Access to Electricity',
            'access_roads_transport': 'Access to Roads/Transport',
            'access_communication': 'Access to Communication',
            'religious_leaders_count': 'Number of Religious Leaders',
        }