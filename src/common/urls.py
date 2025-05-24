from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('communities/', views.communities_home, name='communities_home'),
    path('communities/add/', views.communities_add, name='communities_add'),
    path('communities/manage/', views.communities_manage, name='communities_manage'),
    path('communities/stakeholders/', views.communities_stakeholders, name='communities_stakeholders'),
    path('mana/', views.mana_home, name='mana_home'),
    path('mana/new-assessment/', views.mana_new_assessment, name='mana_new_assessment'),
    path('mana/manage-assessments/', views.mana_manage_assessments, name='mana_manage_assessments'),
    path('mana/geographic-data/', views.mana_geographic_data, name='mana_geographic_data'),
    path('coordination/', views.coordination_home, name='coordination_home'),
    path('coordination/organizations/', views.coordination_organizations, name='coordination_organizations'),
    path('coordination/partnerships/', views.coordination_partnerships, name='coordination_partnerships'),
    path('coordination/events/', views.coordination_events, name='coordination_events'),
    path('coordination/view-all/', views.coordination_view_all, name='coordination_view_all'),
    path('policy-tracking/', views.policy_tracking_home, name='policy_tracking_home'),
    path('policy-tracking/new-policy/', views.policy_tracking_new_policy, name='policy_tracking_new_policy'),
    path('policy-tracking/manage-policies/', views.policy_tracking_manage_policies, name='policy_tracking_manage_policies'),
    path('', views.dashboard, name='home'),  # Default to dashboard
]