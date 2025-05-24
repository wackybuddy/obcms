from django.core.management.base import BaseCommand
from django.db import transaction
from communities.models import OBCCommunity, Stakeholder, StakeholderEngagement
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Populate sample stakeholder data for existing OBC communities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing stakeholder data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing stakeholder data...')
            StakeholderEngagement.objects.all().delete()
            Stakeholder.objects.all().delete()
            self.stdout.write(self.style.WARNING('Existing stakeholder data cleared.'))

        with transaction.atomic():
            self.create_sample_stakeholders()
            self.create_sample_engagements()

        self.stdout.write(self.style.SUCCESS('Sample stakeholder data created successfully!'))

    def create_sample_stakeholders(self):
        """Create sample stakeholders for existing communities."""
        self.stdout.write('Creating sample stakeholders...')
        
        communities = OBCCommunity.objects.all()
        if not communities.exists():
            self.stdout.write(self.style.ERROR('No communities found. Please run populate_sample_communities first.'))
            return

        stakeholder_templates = [
            # Tausug Community Stakeholders
            {
                'community_name': 'Tausug Bangsamoro Village',
                'stakeholders': [
                    {
                        'full_name': 'Haji Abdullah Bin Jamil',
                        'nickname': 'Haji Abdullah',
                        'stakeholder_type': 'community_leader',
                        'position': 'Pangkuluman (Community Leader)',
                        'contact_number': '+63917-555-0101',
                        'email': 'haji.abdullah@example.com',
                        'influence_level': 'very_high',
                        'engagement_level': 'very_active',
                        'areas_of_influence': 'Overall community governance, conflict resolution, cultural preservation',
                        'age': 58,
                        'educational_background': 'Islamic Studies, Community Leadership Training',
                        'cultural_background': 'Tausug',
                        'languages_spoken': 'Tausug, Filipino, English, Arabic',
                        'since_year': 2015,
                        'years_in_community': 35,
                        'special_skills': 'Traditional mediation, Islamic law knowledge, cultural ceremonies',
                        'achievements': 'Successfully mediated 50+ community disputes, established community peace council',
                        'is_verified': True,
                    },
                    {
                        'full_name': 'Ustadz Muhammad Hassan',
                        'nickname': 'Ustadz Hassan',
                        'stakeholder_type': 'imam',
                        'position': 'Imam of Masjid Al-Tausug',
                        'contact_number': '+63917-555-0102',
                        'influence_level': 'high',
                        'engagement_level': 'very_active',
                        'areas_of_influence': 'Religious matters, youth guidance, Islamic education',
                        'age': 45,
                        'educational_background': 'Al-Azhar University Graduate, Islamic Theology',
                        'cultural_background': 'Tausug',
                        'languages_spoken': 'Tausug, Arabic, Filipino, English',
                        'since_year': 2018,
                        'years_in_community': 20,
                        'special_skills': 'Quranic recitation, Islamic jurisprudence, community counseling',
                        'achievements': 'Established madrasah program, trained 20+ young Quranic reciters',
                        'is_verified': True,
                    },
                    {
                        'full_name': 'Bai Fatima Bint Omar',
                        'nickname': 'Bai Fatima',
                        'stakeholder_type': 'women_leader',
                        'position': 'President of Tausug Women\'s Association',
                        'contact_number': '+63917-555-0103',
                        'email': 'fatima.omar@example.com',
                        'influence_level': 'high',
                        'engagement_level': 'active',
                        'areas_of_influence': 'Women\'s rights, livelihood programs, cultural preservation',
                        'age': 42,
                        'educational_background': 'College Graduate, Gender and Development Training',
                        'cultural_background': 'Tausug',
                        'languages_spoken': 'Tausug, Filipino, English',
                        'since_year': 2020,
                        'years_in_community': 25,
                        'special_skills': 'Traditional weaving, microfinance management, community organizing',
                        'achievements': 'Established women\'s cooperative with 100+ members, cultural dance preservation program',
                        'is_verified': True,
                    },
                    {
                        'full_name': 'Ahmad Jalil Bin Said',
                        'nickname': 'Brother Ahmad',
                        'stakeholder_type': 'youth_leader',
                        'position': 'Youth Council Chairperson',
                        'contact_number': '+63917-555-0104',
                        'email': 'ahmad.jalil@example.com',
                        'influence_level': 'medium',
                        'engagement_level': 'very_active',
                        'areas_of_influence': 'Youth programs, sports activities, cultural events',
                        'age': 28,
                        'educational_background': 'College Graduate, Youth Leadership Training',
                        'cultural_background': 'Tausug',
                        'languages_spoken': 'Tausug, Filipino, English',
                        'since_year': 2022,
                        'years_in_community': 28,
                        'special_skills': 'Event organization, social media management, sports coaching',
                        'achievements': 'Organized 5+ youth festivals, established basketball league',
                        'is_verified': True,
                    }
                ]
            },
            # Maguindanao Community Stakeholders
            {
                'community_name': 'Maguindanao Settlers Community',
                'stakeholders': [
                    {
                        'full_name': 'Datu Salipada Pendatun III',
                        'nickname': 'Datu Salipada',
                        'stakeholder_type': 'tribal_leader',
                        'position': 'Traditional Datu',
                        'contact_number': '+63917-555-0201',
                        'influence_level': 'very_high',
                        'engagement_level': 'active',
                        'areas_of_influence': 'Traditional governance, ancestral domain, tribal customs',
                        'age': 62,
                        'educational_background': 'Traditional Leadership, Customary Law',
                        'cultural_background': 'Maguindanao',
                        'languages_spoken': 'Maguindanao, Filipino, English',
                        'since_year': 2010,
                        'years_in_community': 40,
                        'special_skills': 'Traditional conflict resolution, ancestral knowledge, tribal ceremonies',
                        'achievements': 'Preserved tribal customs, established cultural center',
                        'is_verified': True,
                    },
                    {
                        'full_name': 'Ustadz Ibrahim Manguda',
                        'nickname': 'Ustadz Ibrahim',
                        'stakeholder_type': 'ustadz',
                        'position': 'Religious Teacher and Counselor',
                        'contact_number': '+63917-555-0202',
                        'influence_level': 'high',
                        'engagement_level': 'very_active',
                        'areas_of_influence': 'Islamic education, community guidance, religious ceremonies',
                        'age': 50,
                        'educational_background': 'Islamic University Graduate, Religious Studies',
                        'cultural_background': 'Maguindanao',
                        'languages_spoken': 'Maguindanao, Arabic, Filipino',
                        'since_year': 2016,
                        'years_in_community': 15,
                        'special_skills': 'Islamic counseling, Arabic instruction, religious ceremony guidance',
                        'achievements': 'Established Islamic school, trained 30+ religious students',
                        'is_verified': True,
                    },
                    {
                        'full_name': 'Bai Normina Mama',
                        'nickname': 'Ina Normina',
                        'stakeholder_type': 'health_worker',
                        'position': 'Barangay Health Worker',
                        'contact_number': '+63917-555-0203',
                        'influence_level': 'medium',
                        'engagement_level': 'very_active',
                        'areas_of_influence': 'Community health, maternal care, health education',
                        'age': 38,
                        'educational_background': 'Midwifery Training, Community Health Program',
                        'cultural_background': 'Maguindanao',
                        'languages_spoken': 'Maguindanao, Filipino',
                        'since_year': 2019,
                        'years_in_community': 20,
                        'special_skills': 'Traditional healing, midwifery, health education',
                        'achievements': 'Delivered 100+ babies safely, reduced child mortality in community',
                        'is_verified': True,
                    }
                ]
            },
            # Tboli-Muslim Community Stakeholders
            {
                'community_name': 'Tboli-Muslim Unity Settlement',
                'stakeholders': [
                    {
                        'full_name': 'Musa Tboli-Abdullah',
                        'nickname': 'Datu Musa',
                        'stakeholder_type': 'community_leader',
                        'position': 'Inter-Cultural Community Leader',
                        'contact_number': '+63917-555-0301',
                        'email': 'musa.tboli@example.com',
                        'influence_level': 'very_high',
                        'engagement_level': 'very_active',
                        'areas_of_influence': 'Inter-tribal relations, cultural integration, conflict resolution',
                        'age': 55,
                        'educational_background': 'College Graduate, Indigenous Leadership Training',
                        'cultural_background': 'Tboli-Muslim',
                        'languages_spoken': 'Tboli, Hiligaynon, Filipino, English',
                        'since_year': 2012,
                        'years_in_community': 30,
                        'special_skills': 'Cultural mediation, traditional crafts, inter-faith dialogue',
                        'achievements': 'Established peaceful coexistence between Tboli and Muslim residents',
                        'is_verified': True,
                    },
                    {
                        'full_name': 'Sister Maria Consolacion',
                        'nickname': 'Sister Maria',
                        'stakeholder_type': 'volunteer',
                        'position': 'Community Development Worker',
                        'contact_number': '+63917-555-0302',
                        'email': 'sr.maria@example.com',
                        'influence_level': 'high',
                        'engagement_level': 'very_active',
                        'areas_of_influence': 'Education, livelihood training, social services',
                        'age': 47,
                        'educational_background': 'Master\'s in Social Work, Community Development',
                        'cultural_background': 'Cebuano',
                        'languages_spoken': 'Cebuano, Tboli, Hiligaynon, Filipino, English',
                        'since_year': 2017,
                        'years_in_community': 8,
                        'special_skills': 'Social work, livelihood training, project management',
                        'achievements': 'Established scholarship program for indigenous children',
                        'is_verified': True,
                    },
                    {
                        'full_name': 'Ahmad Santos-Usman',
                        'nickname': 'Kuya Ahmad',
                        'stakeholder_type': 'arabic_teacher',
                        'position': 'ALIVE Arabic Teacher',
                        'contact_number': '+63917-555-0303',
                        'influence_level': 'medium',
                        'engagement_level': 'active',
                        'areas_of_influence': 'Islamic education, Arabic literacy, youth guidance',
                        'age': 35,
                        'educational_background': 'ALIVE Program Graduate, Arabic Studies',
                        'cultural_background': 'Tboli-Muslim',
                        'languages_spoken': 'Tboli, Arabic, Filipino, English',
                        'since_year': 2020,
                        'years_in_community': 15,
                        'special_skills': 'Arabic instruction, Quranic studies, youth mentoring',
                        'achievements': 'Taught Arabic to 50+ community members, established reading program',
                        'is_verified': True,
                    }
                ]
            }
        ]

        for community_data in stakeholder_templates:
            try:
                community = communities.get(name=community_data['community_name'])
                self.stdout.write(f'Creating stakeholders for {community.name}...')
                
                for stakeholder_data in community_data['stakeholders']:
                    stakeholder_data['community'] = community
                    if 'verification_date' not in stakeholder_data and stakeholder_data.get('is_verified'):
                        stakeholder_data['verification_date'] = date.today() - timedelta(days=random.randint(30, 365))
                    
                    stakeholder, created = Stakeholder.objects.get_or_create(
                        full_name=stakeholder_data['full_name'],
                        community=community,
                        defaults=stakeholder_data
                    )
                    
                    if created:
                        self.stdout.write(f'  Created: {stakeholder.display_name} ({stakeholder.get_stakeholder_type_display()})')
                    else:
                        self.stdout.write(f'  Already exists: {stakeholder.display_name}')
                        
            except OBCCommunity.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Community "{community_data["community_name"]}" not found. Skipping...'))

    def create_sample_engagements(self):
        """Create sample stakeholder engagements."""
        self.stdout.write('Creating sample engagements...')
        
        stakeholders = Stakeholder.objects.all()
        if not stakeholders.exists():
            self.stdout.write(self.style.WARNING('No stakeholders found. Skipping engagement creation.'))
            return

        engagement_templates = [
            {
                'engagement_type': 'meeting',
                'title': 'Monthly Community Leaders Meeting',
                'description': 'Regular monthly meeting to discuss community issues and development plans.',
                'location': 'Community Center',
                'participants_count': 15,
                'outcome': 'positive',
                'key_points': 'Discussed infrastructure needs, planned cultural festival, addressed security concerns',
                'action_items': 'Follow up with LGU on road repair, organize festival committee, coordinate with police',
                'documented_by': 'Community Secretary'
            },
            {
                'engagement_type': 'consultation',
                'title': 'Livelihood Development Consultation',
                'description': 'Consultation on potential livelihood programs for community members.',
                'location': 'Barangay Hall',
                'participants_count': 25,
                'outcome': 'very_positive',
                'key_points': 'Identified interest in agricultural training, discussed microfinance options',
                'action_items': 'Contact agricultural extension office, research microfinance providers',
                'documented_by': 'OOBC Field Officer'
            },
            {
                'engagement_type': 'training',
                'title': 'Leadership Skills Workshop',
                'description': 'Training workshop on leadership and community organizing skills.',
                'location': 'Municipal Hall',
                'participants_count': 20,
                'outcome': 'positive',
                'key_points': 'Enhanced leadership capabilities, improved communication skills',
                'action_items': 'Apply learned skills in community projects, mentor other leaders',
                'documented_by': 'Training Facilitator'
            },
            {
                'engagement_type': 'religious_activity',
                'title': 'Interfaith Peace Dialogue',
                'description': 'Dialogue session between different religious groups to promote understanding and peace.',
                'location': 'Community Mosque',
                'participants_count': 40,
                'outcome': 'very_positive',
                'key_points': 'Strengthened interfaith relations, planned joint community service project',
                'action_items': 'Organize joint cleanup drive, schedule regular dialogue sessions',
                'documented_by': 'Religious Affairs Coordinator'
            },
            {
                'engagement_type': 'assessment',
                'title': 'Community Needs Assessment',
                'description': 'Comprehensive assessment of community needs and resources.',
                'location': 'Various locations within community',
                'participants_count': 50,
                'outcome': 'positive',
                'key_points': 'Identified priority needs: water system, health services, education facilities',
                'action_items': 'Develop project proposals, seek funding sources, coordinate with government agencies',
                'documented_by': 'Assessment Team Lead'
            }
        ]

        # Create engagements for each stakeholder
        for stakeholder in stakeholders:
            # Create 2-4 engagements per stakeholder
            num_engagements = random.randint(2, 4)
            
            for i in range(num_engagements):
                template = random.choice(engagement_templates)
                
                # Generate random date within last 6 months
                days_ago = random.randint(1, 180)
                engagement_date = date.today() - timedelta(days=days_ago)
                
                engagement_data = template.copy()
                engagement_data.update({
                    'stakeholder': stakeholder,
                    'date': engagement_date,
                    'duration_hours': round(random.uniform(1.0, 4.0), 1),
                    'follow_up_needed': random.choice([True, False]),
                })
                
                if engagement_data['follow_up_needed']:
                    engagement_data['follow_up_date'] = engagement_date + timedelta(days=random.randint(7, 30))
                
                engagement, created = StakeholderEngagement.objects.get_or_create(
                    stakeholder=stakeholder,
                    title=engagement_data['title'],
                    date=engagement_date,
                    defaults=engagement_data
                )
                
                if created:
                    self.stdout.write(f'  Created engagement: {engagement.title} for {stakeholder.display_name}')

        self.stdout.write(f'Created {StakeholderEngagement.objects.count()} sample engagements.')