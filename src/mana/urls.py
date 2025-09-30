from django.urls import path

from . import facilitator_views, participant_views

app_name = "mana"

urlpatterns = [
    # Participant-facing routes
    path(
        "assessments/<uuid:assessment_id>/participant/onboarding/",
        participant_views.participant_onboarding,
        name="participant_onboarding",
    ),
    path(
        "assessments/<uuid:assessment_id>/participant/dashboard/",
        participant_views.participant_dashboard,
        name="participant_dashboard",
    ),
    path(
        "assessments/<uuid:assessment_id>/participant/workshops/<str:workshop_type>/",
        participant_views.participant_workshop_detail,
        name="participant_workshop_detail",
    ),
    # Facilitator routes
    path(
        "assessments/<uuid:assessment_id>/facilitator/dashboard/",
        facilitator_views.facilitator_dashboard,
        name="facilitator_dashboard",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/participants/",
        facilitator_views.manage_participants,
        name="facilitator_manage_participants",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/participants/<int:participant_id>/reset/",
        facilitator_views.reset_participant_progress,
        name="facilitator_reset_participant",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/workshops/<str:workshop_type>/advance/",
        facilitator_views.advance_workshop,
        name="facilitator_advance_workshop",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/workshops/<str:workshop_type>/synthesis/",
        facilitator_views.generate_synthesis,
        name="facilitator_generate_synthesis",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/synthesis/<int:synthesis_id>/regenerate/",
        facilitator_views.regenerate_synthesis,
        name="facilitator_regenerate_synthesis",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/synthesis/<int:synthesis_id>/approve/",
        facilitator_views.approve_synthesis,
        name="facilitator_approve_synthesis",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/exports/<str:workshop_type>/<str:format_type>/",
        facilitator_views.export_workshop_responses,
        name="facilitator_export_workshop",
    ),
]
