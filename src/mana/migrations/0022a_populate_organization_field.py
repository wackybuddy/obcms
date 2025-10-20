# Generated manually for BMMS Phase 6 - Populate organization field
from django.db import migrations


def populate_organization_field(apps, schema_editor):
    """
    Populate organization field with default OOBC organization for all existing records.
    This migration runs after adding the nullable organization field (0022)
    and before making it required (0023).
    """
    Organization = apps.get_model('organizations', 'Organization')

    # Get model classes
    Assessment = apps.get_model('mana', 'Assessment')
    AssessmentCategory = apps.get_model('mana', 'AssessmentCategory')
    AssessmentTeamMember = apps.get_model('mana', 'AssessmentTeamMember')
    BaselineDataCollection = apps.get_model('mana', 'BaselineDataCollection')
    BaselineIndicator = apps.get_model('mana', 'BaselineIndicator')
    BaselineStudy = apps.get_model('mana', 'BaselineStudy')
    BaselineStudyTeamMember = apps.get_model('mana', 'BaselineStudyTeamMember')
    CommunityAspirations = apps.get_model('mana', 'CommunityAspirations')
    CommunityChallenges = apps.get_model('mana', 'CommunityChallenges')
    CommunityGovernance = apps.get_model('mana', 'CommunityGovernance')
    CommunityProfile = apps.get_model('mana', 'CommunityProfile')
    FacilitatorAssessmentAssignment = apps.get_model('mana', 'FacilitatorAssessmentAssignment')
    MANAReport = apps.get_model('mana', 'MANAReport')
    MappingActivity = apps.get_model('mana', 'MappingActivity')
    Need = apps.get_model('mana', 'Need')
    NeedsPrioritization = apps.get_model('mana', 'NeedsPrioritization')
    NeedsPrioritizationItem = apps.get_model('mana', 'NeedsPrioritizationItem')
    NeedVote = apps.get_model('mana', 'NeedVote')
    Survey = apps.get_model('mana', 'Survey')
    SurveyQuestion = apps.get_model('mana', 'SurveyQuestion')
    SurveyResponse = apps.get_model('mana', 'SurveyResponse')
    WorkshopActivity = apps.get_model('mana', 'WorkshopActivity')
    WorkshopNotification = apps.get_model('mana', 'WorkshopNotification')
    WorkshopOutput = apps.get_model('mana', 'WorkshopOutput')
    WorkshopParticipant = apps.get_model('mana', 'WorkshopParticipant')
    WorkshopParticipantAccount = apps.get_model('mana', 'WorkshopParticipantAccount')
    WorkshopQuestionDefinition = apps.get_model('mana', 'WorkshopQuestionDefinition')
    WorkshopResponse = apps.get_model('mana', 'WorkshopResponse')
    WorkshopSession = apps.get_model('mana', 'WorkshopSession')
    WorkshopSynthesis = apps.get_model('mana', 'WorkshopSynthesis')

    # Get or create the default OOBC organization
    oobc_org, created = Organization.objects.get_or_create(
        code='OOBC',
        defaults={
            'name': 'Office for Other Bangsamoro Communities',
            'organization_type': 'PRIMARY',
            'is_active': True,
        }
    )

    # Populate organization field for all models with NULL values
    models_to_update = [
        Assessment,
        AssessmentCategory,
        AssessmentTeamMember,
        BaselineDataCollection,
        BaselineIndicator,
        BaselineStudy,
        BaselineStudyTeamMember,
        CommunityAspirations,
        CommunityChallenges,
        CommunityGovernance,
        CommunityProfile,
        FacilitatorAssessmentAssignment,
        MANAReport,
        MappingActivity,
        Need,
        NeedsPrioritization,
        NeedsPrioritizationItem,
        NeedVote,
        Survey,
        SurveyQuestion,
        SurveyResponse,
        WorkshopActivity,
        WorkshopNotification,
        WorkshopOutput,
        WorkshopParticipant,
        WorkshopParticipantAccount,
        WorkshopQuestionDefinition,
        WorkshopResponse,
        WorkshopSession,
        WorkshopSynthesis,
    ]

    for model in models_to_update:
        updated_count = model.objects.filter(organization__isnull=True).update(
            organization=oobc_org
        )
        if updated_count > 0:
            print(f"✅ Populated {updated_count} {model.__name__} records with OOBC organization")


def reverse_populate(apps, schema_editor):
    """
    Reverse migration - set organization field back to NULL.
    """
    Assessment = apps.get_model('mana', 'Assessment')
    AssessmentCategory = apps.get_model('mana', 'AssessmentCategory')
    AssessmentTeamMember = apps.get_model('mana', 'AssessmentTeamMember')
    BaselineDataCollection = apps.get_model('mana', 'BaselineDataCollection')
    BaselineIndicator = apps.get_model('mana', 'BaselineIndicator')
    BaselineStudy = apps.get_model('mana', 'BaselineStudy')
    BaselineStudyTeamMember = apps.get_model('mana', 'BaselineStudyTeamMember')
    CommunityAspirations = apps.get_model('mana', 'CommunityAspirations')
    CommunityChallenges = apps.get_model('mana', 'CommunityChallenges')
    CommunityGovernance = apps.get_model('mana', 'CommunityGovernance')
    CommunityProfile = apps.get_model('mana', 'CommunityProfile')
    FacilitatorAssessmentAssignment = apps.get_model('mana', 'FacilitatorAssessmentAssignment')
    MANAReport = apps.get_model('mana', 'MANAReport')
    MappingActivity = apps.get_model('mana', 'MappingActivity')
    Need = apps.get_model('mana', 'Need')
    NeedsPrioritization = apps.get_model('mana', 'NeedsPrioritization')
    NeedsPrioritizationItem = apps.get_model('mana', 'NeedsPrioritizationItem')
    NeedVote = apps.get_model('mana', 'NeedVote')
    Survey = apps.get_model('mana', 'Survey')
    SurveyQuestion = apps.get_model('mana', 'SurveyQuestion')
    SurveyResponse = apps.get_model('mana', 'SurveyResponse')
    WorkshopActivity = apps.get_model('mana', 'WorkshopActivity')
    WorkshopNotification = apps.get_model('mana', 'WorkshopNotification')
    WorkshopOutput = apps.get_model('mana', 'WorkshopOutput')
    WorkshopParticipant = apps.get_model('mana', 'WorkshopParticipant')
    WorkshopParticipantAccount = apps.get_model('mana', 'WorkshopParticipantAccount')
    WorkshopQuestionDefinition = apps.get_model('mana', 'WorkshopQuestionDefinition')
    WorkshopResponse = apps.get_model('mana', 'WorkshopResponse')
    WorkshopSession = apps.get_model('mana', 'WorkshopSession')
    WorkshopSynthesis = apps.get_model('mana', 'WorkshopSynthesis')

    models_to_update = [
        Assessment,
        AssessmentCategory,
        AssessmentTeamMember,
        BaselineDataCollection,
        BaselineIndicator,
        BaselineStudy,
        BaselineStudyTeamMember,
        CommunityAspirations,
        CommunityChallenges,
        CommunityGovernance,
        CommunityProfile,
        FacilitatorAssessmentAssignment,
        MANAReport,
        MappingActivity,
        Need,
        NeedsPrioritization,
        NeedsPrioritizationItem,
        NeedVote,
        Survey,
        SurveyQuestion,
        SurveyResponse,
        WorkshopActivity,
        WorkshopNotification,
        WorkshopOutput,
        WorkshopParticipant,
        WorkshopParticipantAccount,
        WorkshopQuestionDefinition,
        WorkshopResponse,
        WorkshopSession,
        WorkshopSynthesis,
    ]

    for model in models_to_update:
        model.objects.all().update(organization=None)


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('mana', '0022_add_organization_field_nullable'),
    ]

    operations = [
        migrations.RunPython(populate_organization_field, reverse_populate),
    ]
