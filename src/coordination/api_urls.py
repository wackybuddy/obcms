from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    StakeholderEngagementTypeViewSet, StakeholderEngagementViewSet,
    EngagementFacilitatorViewSet, ConsultationFeedbackViewSet,
    EngagementTrackingViewSet, OrganizationViewSet, OrganizationContactViewSet,
    CommunicationViewSet, CommunicationTemplateViewSet, CommunicationScheduleViewSet,
    EventViewSet, EventParticipantViewSet, ActionItemViewSet, EventDocumentViewSet,
    PartnershipViewSet, PartnershipSignatoryViewSet, PartnershipMilestoneViewSet,
    PartnershipDocumentViewSet
)

app_name = 'coordination_api'

router = DefaultRouter()
router.register(r'stakeholder-engagement-types', StakeholderEngagementTypeViewSet)
router.register(r'stakeholder-engagements', StakeholderEngagementViewSet)
router.register(r'engagement-facilitators', EngagementFacilitatorViewSet)
router.register(r'consultation-feedback', ConsultationFeedbackViewSet)
router.register(r'engagement-tracking', EngagementTrackingViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'organization-contacts', OrganizationContactViewSet)
router.register(r'communications', CommunicationViewSet)
router.register(r'communication-templates', CommunicationTemplateViewSet)
router.register(r'communication-schedules', CommunicationScheduleViewSet)
router.register(r'events', EventViewSet)
router.register(r'event-participants', EventParticipantViewSet)
router.register(r'action-items', ActionItemViewSet)
router.register(r'event-documents', EventDocumentViewSet)
router.register(r'partnerships', PartnershipViewSet)
router.register(r'partnership-signatories', PartnershipSignatoryViewSet)
router.register(r'partnership-milestones', PartnershipMilestoneViewSet)
router.register(r'partnership-documents', PartnershipDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]