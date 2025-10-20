# Generated manually for BMMS Phase 5 - Populate organization field
from django.db import migrations


def populate_organization_field(apps, schema_editor):
    """
    Populate organization field with default OOBC organization for all existing records.
    This migration runs after adding the nullable organization field (0029)
    and before making it required (0030).
    """
    Organization = apps.get_model('organizations', 'Organization')
    OBCCommunity = apps.get_model('communities', 'OBCCommunity')
    CommunityLivelihood = apps.get_model('communities', 'CommunityLivelihood')
    CommunityInfrastructure = apps.get_model('communities', 'CommunityInfrastructure')
    Stakeholder = apps.get_model('communities', 'Stakeholder')
    StakeholderEngagement = apps.get_model('communities', 'StakeholderEngagement')
    MunicipalityCoverage = apps.get_model('communities', 'MunicipalityCoverage')
    ProvinceCoverage = apps.get_model('communities', 'ProvinceCoverage')
    GeographicDataLayer = apps.get_model('communities', 'GeographicDataLayer')
    MapVisualization = apps.get_model('communities', 'MapVisualization')
    SpatialDataPoint = apps.get_model('communities', 'SpatialDataPoint')
    CommunityEvent = apps.get_model('communities', 'CommunityEvent')

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
        OBCCommunity,
        CommunityLivelihood,
        CommunityInfrastructure,
        Stakeholder,
        StakeholderEngagement,
        MunicipalityCoverage,
        ProvinceCoverage,
        GeographicDataLayer,
        MapVisualization,
        SpatialDataPoint,
        CommunityEvent,
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
    OBCCommunity = apps.get_model('communities', 'OBCCommunity')
    CommunityLivelihood = apps.get_model('communities', 'CommunityLivelihood')
    CommunityInfrastructure = apps.get_model('communities', 'CommunityInfrastructure')
    Stakeholder = apps.get_model('communities', 'Stakeholder')
    StakeholderEngagement = apps.get_model('communities', 'StakeholderEngagement')
    MunicipalityCoverage = apps.get_model('communities', 'MunicipalityCoverage')
    ProvinceCoverage = apps.get_model('communities', 'ProvinceCoverage')
    GeographicDataLayer = apps.get_model('communities', 'GeographicDataLayer')
    MapVisualization = apps.get_model('communities', 'MapVisualization')
    SpatialDataPoint = apps.get_model('communities', 'SpatialDataPoint')
    CommunityEvent = apps.get_model('communities', 'CommunityEvent')

    models_to_update = [
        OBCCommunity,
        CommunityLivelihood,
        CommunityInfrastructure,
        Stakeholder,
        StakeholderEngagement,
        MunicipalityCoverage,
        ProvinceCoverage,
        GeographicDataLayer,
        MapVisualization,
        SpatialDataPoint,
        CommunityEvent,
    ]

    for model in models_to_update:
        model.objects.all().update(organization=None)


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('communities', '0029_add_organization_field'),
    ]

    operations = [
        migrations.RunPython(populate_organization_field, reverse_populate),
    ]
