"""Management command to create comprehensive test data for MANA regional workshops."""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils import timezone
from datetime import timedelta

from common.models import Province, Region
from mana.models import (
    Assessment,
    AssessmentCategory,
    FacilitatorAssessmentAssignment,
    WorkshopActivity,
    WorkshopParticipantAccount,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Create test data for MANA regional workshop system"

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing test data before creating new',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== MANA Regional Workshop Test Data Setup ===\n'))

        if options['reset']:
            self.stdout.write('Resetting test data...')
            self._reset_test_data()

        # Get or create provinces
        provinces = self._setup_provinces()

        # Create test users
        admin_user = self._create_admin_user()
        facilitator1, facilitator2 = self._create_facilitators()
        participants = self._create_participants(provinces, admin_user)

        # Create assessments
        assessments = self._create_assessments(provinces, admin_user)

        # Assign facilitators to assessments
        self._assign_facilitators(facilitator1, facilitator2, assessments)

        # Create workshop activities
        self._create_workshop_activities(assessments, admin_user)

        # Enroll participants
        self._enroll_participants(participants, assessments, admin_user)

        self.stdout.write(self.style.SUCCESS('\n✅ Test data setup complete!\n'))
        self._print_summary(admin_user, facilitator1, facilitator2, participants, assessments)

    def _reset_test_data(self):
        """Delete test users and related data in correct order."""
        # Delete assessments first (cascades to FacilitatorAssessmentAssignment, WorkshopActivity, etc.)
        Assessment.objects.filter(title__startswith='[TEST]').delete()
        # Now safe to delete users
        User.objects.filter(username__startswith='test_').delete()

    def _setup_provinces(self):
        """Get provinces for testing - one per region."""
        # 4 regions with representative provinces
        region_config = {
            'Region IX': {'name': 'Zamboanga Peninsula', 'code': 'IX', 'province': 'Zamboanga del Sur'},
            'Region X': {'name': 'Northern Mindanao', 'code': 'X', 'province': 'Bukidnon'},
            'Region XII': {'name': 'SOCCSKSARGEN', 'code': 'XII', 'province': 'Cotabato'},
            'Region XIII': {'name': 'Caraga', 'code': 'XIII', 'province': 'Agusan del Sur'},
        }

        provinces = {}

        for region_key, config in region_config.items():
            # Get or create region
            region, region_created = Region.objects.get_or_create(
                code=config['code'],
                defaults={
                    'name': config['name'],
                }
            )

            if region_created:
                self.stdout.write(f'  Created region: {region.name} ({region.code})')

            # Get or create province
            province = Province.objects.filter(name=config['province']).first()

            if not province:
                self.stdout.write(self.style.WARNING(
                    f'  Warning: Province "{config["province"]}" not found. Creating dummy province.'
                ))
                province = Province.objects.create(
                    name=config['province'],
                    code=config['province'][:3].upper(),
                    region=region
                )

            provinces[region_key] = province

        return provinces

    def _create_admin_user(self):
        """Create admin user for test data creation."""
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@oobc.gov.ph',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )

        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'  Created admin user: admin / admin123')
        else:
            self.stdout.write(f'  Admin user already exists')

        return admin

    def _create_facilitators(self):
        """Create facilitator test accounts."""
        facilitators = []

        for i in [1, 2]:
            user, created = User.objects.get_or_create(
                username=f'test_facilitator{i}',
                defaults={
                    'email': f'facilitator{i}@test.oobc.gov.ph',
                    'first_name': f'Facilitator',
                    'last_name': f'Test{i}',
                }
            )

            if created:
                user.set_password('password123')
                user.save()

                # Grant facilitator permission
                permission = Permission.objects.get(codename='can_facilitate_workshop')
                user.user_permissions.add(permission)

                self.stdout.write(f'  Created facilitator: test_facilitator{i} / password123')
            else:
                self.stdout.write(f'  Facilitator test_facilitator{i} already exists')

            facilitators.append(user)

        return tuple(facilitators)

    def _create_participants(self, provinces, admin_user):
        """Create 30 participant test accounts per region (120 total)."""
        participants = []
        stakeholder_types = ['elder', 'women_leader', 'youth_leader', 'farmer', 'religious_leader',
                             'business_owner', 'teacher', 'health_worker']

        regions = list(provinces.keys())
        province_list = list(provinces.values())

        # Create 30 participants per region = 120 total
        for i in range(1, 121):
            user, created = User.objects.get_or_create(
                username=f'test_participant{i:03d}',
                defaults={
                    'email': f'participant{i:03d}@test.oobc.gov.ph',
                    'first_name': f'Participant',
                    'last_name': f'Test{i:03d}',
                }
            )

            if created:
                user.set_password('password123')
                user.save()

                if i % 30 == 1:
                    self.stdout.write(f'  Creating participants {i:03d} to {min(i+29, 120):03d}...')
            elif i == 1:
                self.stdout.write(f'  Participants already exist, skipping creation messages...')

            # Assign to province/region
            region_index = (i - 1) // 30  # 0-3 for 4 regions
            province = province_list[region_index]
            region = regions[region_index]

            participants.append({
                'user': user,
                'stakeholder_type': stakeholder_types[i % len(stakeholder_types)],
                'province': province,
                'region': region,
            })

        self.stdout.write(f'  ✅ Total participants ready: {len(participants)}')
        return participants

    def _create_assessments(self, provinces, admin_user):
        """Create 4 regional workshop assessments (one per region)."""
        # Get or create AssessmentCategory
        category, category_created = AssessmentCategory.objects.get_or_create(
            name='Regional Workshop Assessment',
            defaults={
                'category_type': 'needs_assessment',
                'description': 'Regional MANA workshop assessments for community needs identification',
                'icon': 'fas fa-users',
                'color': '#10B981',  # emerald
                'is_active': True,
            }
        )

        if category_created:
            self.stdout.write(f'  Created assessment category: {category.name}')

        assessments = {}

        for region, province in provinces.items():
            assessment, created = Assessment.objects.get_or_create(
                title=f'[TEST] Regional Workshop - {region} ({province.name}) 2025',
                defaults={
                    'description': f'Test regional MANA workshop assessment for {region}. '
                                   f'This assessment covers {province.name} and surrounding areas.',
                    'category': category,
                    'assessment_level': 'regional',
                    'primary_methodology': 'workshop',
                    'province': province,
                    'created_by': admin_user,
                    'lead_assessor': admin_user,
                    'planned_start_date': timezone.now().date(),
                    'planned_end_date': (timezone.now() + timedelta(days=30)).date(),
                    'status': 'in_progress',
                }
            )

            if created:
                self.stdout.write(f'  Created assessment: {assessment.title}')
            else:
                self.stdout.write(f'  Assessment already exists: {assessment.title}')

            assessments[region] = assessment

        return assessments

    def _assign_facilitators(self, facilitator1, facilitator2, assessments):
        """Assign facilitators to assessments."""
        assessment_list = list(assessments.values())

        # Facilitator 1 gets all 4 assessments
        for assessment in assessment_list:
            FacilitatorAssessmentAssignment.objects.get_or_create(
                facilitator=facilitator1,
                assessment=assessment,
                defaults={'assigned_by': facilitator1}
            )

        self.stdout.write(f'  Assigned facilitator1 to all {len(assessment_list)} assessments')

        # Facilitator 2 gets first 2 assessments
        for assessment in assessment_list[:2]:
            FacilitatorAssessmentAssignment.objects.get_or_create(
                facilitator=facilitator2,
                assessment=assessment,
                defaults={'assigned_by': facilitator1}
            )

        self.stdout.write(f'  Assigned facilitator2 to first 2 assessments')

    def _create_workshop_activities(self, assessments, admin_user):
        """Create 5 workshop activities for each of the 4 assessments."""
        workshops = [
            ('workshop_1', 'Workshop 1: Understanding the Community Context', 'day_2'),
            ('workshop_2', 'Workshop 2: Community Aspirations and Priorities', 'day_3'),
            ('workshop_3', 'Workshop 3: Community Collaboration and Empowerment', 'day_3'),
            ('workshop_4', 'Workshop 4: Community Feedback on Existing Initiatives', 'day_4'),
            ('workshop_5', 'Workshop 5: OBCs Needs, Challenges, Factors, and Outcomes', 'day_4'),
        ]

        for region, assessment in assessments.items():
            for i, (workshop_type, title, day) in enumerate(workshops, 1):
                scheduled_date = timezone.now().date() + timedelta(days=i)
                WorkshopActivity.objects.get_or_create(
                    assessment=assessment,
                    workshop_type=workshop_type,
                    defaults={
                        'title': title,
                        'description': f'Comprehensive {title} session for {region} regional assessment.',
                        'workshop_day': day,
                        'scheduled_date': scheduled_date,
                        'start_time': '09:00:00',
                        'end_time': '16:00:00',
                        'duration_hours': 7.0,  # 9am to 4pm = 7 hours
                        'target_participants': 30,  # 30 participants per region
                        'methodology': 'Participatory workshop with FGD, mapping exercises, and collaborative discussion',
                        'expected_outputs': 'Community context insights, priority needs identification, and stakeholder engagement data',
                        'created_by': admin_user,
                    }
                )

            self.stdout.write(f'  Created 5 workshops for: {region}')

    def _enroll_participants(self, participants, assessments, admin_user):
        """Enroll participants in their respective regional assessments (30 per region)."""
        enrollment_count = {region: 0 for region in assessments.keys()}

        for i, participant_data in enumerate(participants):
            # Get assessment for participant's region
            region = participant_data['region']
            assessment = assessments[region]

            WorkshopParticipantAccount.objects.get_or_create(
                user=participant_data['user'],
                assessment=assessment,
                defaults={
                    'province': participant_data['province'],
                    'stakeholder_type': participant_data['stakeholder_type'],
                    'organization': f'Test Organization {i + 1}',
                    'created_by': admin_user,
                    'current_workshop': 'workshop_1',
                    'facilitator_advanced_to': 'workshop_1',
                    'consent_given': True,
                    'consent_date': timezone.now(),
                    'profile_completed': True,
                }
            )

            enrollment_count[region] += 1

        self.stdout.write(f'  ✅ Enrolled {len(participants)} participants total:')
        for region, count in enrollment_count.items():
            self.stdout.write(f'     - {region}: {count} participants')

    def _print_summary(self, admin, facilitator1, facilitator2, participants, assessments):
        """Print test data summary."""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('\n📊 MANA Regional Workshop Test Data Summary\n'))
        self.stdout.write('=' * 70)

        self.stdout.write(self.style.WARNING('\n🔐 Login Credentials:'))
        self.stdout.write(f'  Admin: admin / admin123')
        self.stdout.write(f'  Facilitator 1: test_facilitator1 / password123 (All 4 assessments)')
        self.stdout.write(f'  Facilitator 2: test_facilitator2 / password123 (First 2 assessments)')
        self.stdout.write(f'  Participants: test_participant001-120 / password123')

        self.stdout.write(self.style.WARNING(f'\n📝 Created Assessments: {len(assessments)}'))
        for region, assessment in assessments.items():
            participant_count = WorkshopParticipantAccount.objects.filter(assessment=assessment).count()
            self.stdout.write(f'  - {assessment.title}')
            self.stdout.write(f'    └─ {participant_count} participants enrolled')

        self.stdout.write(self.style.WARNING(f'\n👥 Total Participants: {len(participants)}'))
        self.stdout.write(f'  - 30 participants per region = 120 total')
        self.stdout.write(f'  - 8 stakeholder types (elder, women_leader, youth_leader, etc.)')

        self.stdout.write(self.style.WARNING(f'\n🎯 Workshop Activities:'))
        self.stdout.write(f'  - 5 workshops per assessment = 20 total workshop activities')
        self.stdout.write(f'  - All participants start at Workshop 1')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('\n✅ Ready for comprehensive testing!'))
        self.stdout.write(self.style.SUCCESS('   - 4 regional assessments covering Regions IX, X, XII, XIII'))
        self.stdout.write(self.style.SUCCESS('   - 30 participants per region for realistic cohort testing'))
        self.stdout.write(self.style.SUCCESS('   - Facilitators can advance cohorts through workshops'))
        self.stdout.write(self.style.SUCCESS('   - Test notification system with large participant groups\n'))