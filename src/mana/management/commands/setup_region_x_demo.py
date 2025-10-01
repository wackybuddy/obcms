"""Management command to create a fully populated Region X demo with workshop submissions."""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from mana.models import (
    Assessment,
    WorkshopActivity,
    WorkshopParticipantAccount,
    WorkshopResponse,
    WorkshopQuestionDefinition,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Create a complete Region X demo with facilitator and participant workshop submissions"

    def add_arguments(self, parser):
        parser.add_argument(
            '--complete-workshop',
            type=int,
            default=1,
            help='Which workshop to complete (1-5)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Region X Demo Setup ===\n'))

        workshop_num = options['complete_workshop']
        workshop_type = f'workshop_{workshop_num}'

        # Get Region X assessment
        assessment = self._get_region_x_assessment()
        if not assessment:
            self.stdout.write(self.style.ERROR('ERROR: Region X assessment not found!'))
            return

        # Get facilitator
        facilitator = self._get_facilitator()

        # Get participants (001-030 are Region IX, so we need different ones)
        # Actually, let me check which participants are for Region X
        participants = self._get_region_x_participants(assessment)

        # Get workshop activity
        workshop = WorkshopActivity.objects.filter(
            assessment=assessment,
            workshop_type=workshop_type
        ).first()

        if not workshop:
            self.stdout.write(self.style.ERROR(f'ERROR: Workshop {workshop_num} not found for Region X!'))
            return

        # Create/get workshop questions
        questions = self._create_workshop_questions(workshop)

        # Generate responses for all 30 participants
        self._generate_participant_responses(participants, workshop, questions)

        self.stdout.write(self.style.SUCCESS('\n✅ Region X Demo Setup Complete!\n'))
        self._print_summary(assessment, facilitator, participants, workshop)

    def _get_region_x_assessment(self):
        """Get the Region X assessment."""
        # Use province name to avoid matching Region XIII which contains 'Region X'
        assessment = Assessment.objects.filter(
            title__contains='Bukidnon',
            title__startswith='[TEST]'
        ).first()

        if not assessment:
            # Fallback: try exact match with Region X
            assessment = Assessment.objects.filter(
                title__contains='Region X (',
                title__startswith='[TEST]'
            ).first()

        if assessment:
            self.stdout.write(f'  ✓ Found assessment: {assessment.title}')
        return assessment

    def _get_facilitator(self):
        """Get test facilitator."""
        facilitator = User.objects.filter(username='test_facilitator1').first()
        if facilitator:
            self.stdout.write(f'  ✓ Using facilitator: {facilitator.username}')
        return facilitator

    def _get_region_x_participants(self, assessment):
        """Get Region X participants."""
        participants = WorkshopParticipantAccount.objects.filter(
            assessment=assessment
        ).select_related('user')

        self.stdout.write(f'  ✓ Found {participants.count()} participants for Region X')
        return list(participants)

    def _create_workshop_questions(self, workshop):
        """Create realistic workshop questions for Workshop 1."""
        questions_data = [
            {
                'question_id': 'q1_basic_services',
                'order': 1,
                'definition': {
                    'type': 'long_text',
                    'text': 'What are the main challenges faced by your community in terms of basic services (education, health, water, electricity)?',
                    'required': True,
                }
            },
            {
                'question_id': 'q2_islamic_education',
                'order': 2,
                'definition': {
                    'type': 'long_text',
                    'text': 'Describe the current state of Islamic education facilities (madrasah, Arabic teachers) in your area.',
                    'required': True,
                }
            },
            {
                'question_id': 'q3_livelihood',
                'order': 3,
                'definition': {
                    'type': 'long_text',
                    'text': 'What are the main sources of livelihood in your community? Are there specific challenges related to economic opportunities?',
                    'required': True,
                }
            },
            {
                'question_id': 'q4_gov_relationship',
                'order': 4,
                'definition': {
                    'type': 'single_choice',
                    'text': 'How would you rate the current relationship between your community and local government?',
                    'required': True,
                    'options': ['Excellent', 'Good', 'Fair', 'Poor', 'Very Poor']
                }
            },
            {
                'question_id': 'q5_cultural_practices',
                'order': 5,
                'definition': {
                    'type': 'long_text',
                    'text': 'What cultural or religious practices are most important to preserve in your community?',
                    'required': True,
                }
            },
            {
                'question_id': 'q6_government_programs',
                'order': 6,
                'definition': {
                    'type': 'long_text',
                    'text': 'Are there any ongoing or past government programs that have benefited your community? What were they?',
                    'required': False,
                }
            },
            {
                'question_id': 'q7_priority_need',
                'order': 7,
                'definition': {
                    'type': 'single_choice',
                    'text': 'What is your community\'s priority need?',
                    'required': True,
                    'options': ['Education', 'Healthcare', 'Infrastructure', 'Livelihood', 'Water/Sanitation', 'Peace and Security']
                }
            },
            {
                'question_id': 'q8_participation',
                'order': 8,
                'definition': {
                    'type': 'long_text',
                    'text': 'How does your community participate in local governance and decision-making processes?',
                    'required': True,
                }
            },
        ]

        questions = []
        for q_data in questions_data:
            question, created = WorkshopQuestionDefinition.objects.get_or_create(
                workshop_type=workshop.workshop_type,
                question_id=q_data['question_id'],
                version='v1',
                defaults={
                    'order': q_data['order'],
                    'definition': q_data['definition']
                }
            )
            questions.append(question)
            if created:
                self.stdout.write(f'  ✓ Created question {q_data["question_id"]}')

        return questions

    def _generate_participant_responses(self, participants, workshop, questions):
        """Generate realistic responses for all participants."""
        response_templates = {
            1: [  # Challenges
                "Our community struggles with limited access to clean water, especially during dry season. The health center is understaffed and lacks essential medicines. Many children walk 5km to reach the nearest secondary school.",
                "Education infrastructure is inadequate with overcrowded classrooms. We have frequent power outages affecting businesses. The road to our barangay is unpaved and becomes impassable during rainy season.",
                "Healthcare services are very limited. We don't have enough teachers in our elementary school. Water supply is inconsistent and many rely on unsafe sources. Electricity reaches only 60% of households.",
                "The main challenges are poor road conditions, lack of potable water systems, inadequate health facilities, and limited access to quality education especially for high school students.",
                "We lack proper sanitation facilities. The health center operates only 2 days a week. School buildings need major repairs. Electricity is unreliable affecting children's ability to study at night.",
            ],
            2: [  # Islamic education
                "We have one madrasah serving 45 students but it lacks proper learning materials. We have 2 Arabic teachers who volunteer their time. The building needs repairs and we need more Quran copies.",
                "Islamic education is primarily taught in homes by volunteer ustadz. We don't have a formal madrasah yet. We have 3 Arabic teachers but they lack teaching materials and proper compensation.",
                "Our madrasah serves 60 children but the facility is too small. We need trained Arabic teachers and updated curriculum materials. The community contributes what they can but resources are limited.",
                "We have a small madrasah run by donations. One ustadz teaches but he also has a farm to support his family. We urgently need learning materials, proper classrooms, and teacher training.",
                "Islamic education is integrated in our mosque activities. We have 2 part-time Arabic teachers. We need a dedicated madrasah building, teaching materials, and support for teacher salaries.",
            ],
            3: [  # Livelihood
                "Most families depend on farming (rice, corn, vegetables). Challenges include lack of irrigation, expensive fertilizers, limited market access, and low farmgate prices. Some do fishing and small trading.",
                "Agriculture is the main source - rice farming and coconut. Problems are lack of farm-to-market roads, no cold storage, middlemen taking most profits, and limited access to credit for capital.",
                "Farming, fishing, and small businesses (sari-sari stores, tricycle driving). Challenges: no access to microfinance, expensive inputs, poor transportation, limited skills training opportunities.",
                "Primary livelihood is agriculture (corn, cassava, vegetables) and livestock. Challenges include climate change affecting crops, lack of irrigation, high input costs, and difficulty accessing markets.",
                "Mixed farming and fishing. Major issues: lack of post-harvest facilities, no farmer cooperatives, expensive farm inputs, limited technical assistance, and exploitation by traders.",
            ],
            4: [  # Government relationship rating
                "Good", "Fair", "Fair", "Good", "Poor", "Fair", "Good", "Fair", "Fair", "Good",
                "Fair", "Poor", "Good", "Fair", "Fair", "Good", "Fair", "Fair", "Good", "Poor",
                "Fair", "Good", "Fair", "Fair", "Good", "Fair", "Poor", "Good", "Fair", "Fair",
            ],
            5: [  # Cultural practices
                "Islamic religious observances (Ramadan, Eid celebrations), traditional wedding ceremonies, madrasah education, Friday congregational prayers, and halal food practices are central to our identity.",
                "Observance of Islamic holy days, traditional conflict resolution through rido settlement, respect for elders, modest dress code, halal food preparation, and Arabic language learning.",
                "Friday prayers, Ramadan fasting, traditional Bangsamoro music and dance, Islamic marriage ceremonies, halal dietary laws, and respect for traditional leaders (datu, imam).",
                "Islamic education from childhood, traditional dispute mediation, celebration of Islamic holidays, preservation of Maguindanao/Maranao language, and traditional crafts like brass work and weaving.",
                "Religious practices (5 daily prayers, Quran recitation), traditional governance through sultans and datus, Islamic marriage customs, halal industry, and teaching children about Bangsamoro history.",
            ],
            6: [  # Government programs
                "The 4Ps program helps families with children in school. We received solar street lights from DILG. The Department of Agriculture provided seeds. BARMM's TABANG program assisted some families.",
                "Pantawid Pamilya (4Ps) supports education. We got water system improvement from LWUA. The health center received medical equipment. Some youth attended TESDA skills training.",
                "4Ps conditional cash transfer program. Free rice distribution during pandemic. Barangay health station improvement. Some farmers got ACPC support for coconut replanting.",
                "Social pension for senior citizens. Scholarship programs for college students. Farm inputs from DA. The PhilHealth expansion helped with hospital bills. Barangay received KALAHI-CIDSS project.",
                "4Ps helps with school expenses. DOLE's TUPAD program provided temporary work. We received relief goods during disasters. Some got livelihood assistance from DSWD. Health insurance coverage improved.",
            ],
            7: [  # Priority need
                "Education", "Healthcare", "Infrastructure", "Livelihood", "Water/Sanitation", "Education",
                "Healthcare", "Infrastructure", "Livelihood", "Education", "Water/Sanitation", "Healthcare",
                "Infrastructure", "Education", "Livelihood", "Healthcare", "Education", "Infrastructure",
                "Livelihood", "Water/Sanitation", "Education", "Healthcare", "Infrastructure", "Education",
                "Livelihood", "Healthcare", "Education", "Infrastructure", "Water/Sanitation", "Education",
            ],
            8: [  # Participation in governance
                "We participate through barangay assemblies and consultations. Community representatives attend municipal planning sessions. Islamic leaders are consulted on cultural matters. Youth and women have representation.",
                "Monthly barangay meetings where residents can voice concerns. We elect barangay officials every 3 years. The barangay council includes IP representatives. However, actual decision-making power is limited.",
                "Through barangay development council meetings, sangguniang barangay sessions (when invited), and community consultations for projects. Traditional leaders also communicate with local officials.",
                "We attend barangay assemblies when called. Community feedback is sometimes sought for projects. However, we feel our input is not always considered in final decisions. More meaningful participation is needed.",
                "Participation mainly through barangay captain who represents us in municipal meetings. We have community consultations for major projects. Traditional governance structures work alongside formal government.",
            ],
        }

        completed_count = 0
        for i, participant in enumerate(participants):
            # Delete existing responses for this workshop
            WorkshopResponse.objects.filter(
                participant=participant,
                workshop=workshop
            ).delete()

            # Create responses for each question
            for question in questions:
                # Extract question number from question_id (e.g., 'q1_basic_services' -> 1)
                question_num = int(question.question_id.split('_')[0][1:])

                # Determine answer based on question type
                question_type = question.definition.get('type', 'long_text')

                if question_type == 'single_choice':
                    # Use template responses for choice questions
                    if question_num == 4:  # Government relationship
                        answer = response_templates[4][i % len(response_templates[4])]
                    elif question_num == 7:  # Priority need
                        answer = response_templates[7][i % len(response_templates[7])]
                    else:
                        # Fallback to random option
                        options = question.definition.get('options', [])
                        answer = random.choice(options) if options else "No answer"
                else:
                    # long_text questions
                    templates = response_templates.get(question_num, ["Response provided."])
                    answer = templates[i % len(templates)]

                WorkshopResponse.objects.create(
                    participant=participant,
                    workshop=workshop,
                    question_id=question.question_id,
                    response_data={'answer': answer},
                    status='submitted',
                    submitted_at=timezone.now() - timedelta(hours=random.randint(1, 48))
                )

            # Update participant status
            participant.completed_workshops = ['workshop_1']
            participant.current_workshop = 'workshop_1'  # Stay at workshop 1 (not advanced yet)
            participant.facilitator_advanced_to = 'workshop_1'
            participant.save(update_fields=['completed_workshops', 'current_workshop', 'facilitator_advanced_to', 'updated_at'])

            completed_count += 1
            if completed_count % 10 == 0:
                self.stdout.write(f'  ✓ Processed {completed_count} participants...')

        self.stdout.write(f'  ✅ Generated responses for all {completed_count} participants')

    def _print_summary(self, assessment, facilitator, participants, workshop):
        """Print demo summary."""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('\n📊 Region X Demo Summary\n'))
        self.stdout.write('=' * 70)

        self.stdout.write(self.style.WARNING(f'\n📝 Assessment:'))
        self.stdout.write(f'  {assessment.title}')
        self.stdout.write(f'  ID: {assessment.id}')

        self.stdout.write(self.style.WARNING(f'\n👤 Facilitator:'))
        self.stdout.write(f'  {facilitator.username} ({facilitator.get_full_name()})')

        self.stdout.write(self.style.WARNING(f'\n👥 Participants:'))
        self.stdout.write(f'  Total: {len(participants)}')
        sample_users = [p.user.username for p in participants[:5]]
        self.stdout.write(f'  Sample: {", ".join(sample_users)}...')

        self.stdout.write(self.style.WARNING(f'\n📋 Workshop Completed:'))
        self.stdout.write(f'  {workshop.title}')
        self.stdout.write(f'  Questions: {WorkshopQuestionDefinition.objects.filter(workshop_type=workshop.workshop_type).count()}')
        self.stdout.write(f'  Total Responses: {WorkshopResponse.objects.filter(workshop=workshop).count()}')
        self.stdout.write(f'  Participants Submitted: {len(participants)}/30')

        self.stdout.write(self.style.WARNING(f'\n🔗 Access URLs:'))
        self.stdout.write(f'  Facilitator Dashboard:')
        self.stdout.write(f'    http://localhost:8000/mana/workshops/assessments/{assessment.id}/facilitator/dashboard/')
        self.stdout.write(f'  First Participant (#{participants[0].user.username}):')
        self.stdout.write(f'    http://localhost:8000/mana/workshops/participant/assessments/')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('\n✅ Region X is ready for testing!'))
        self.stdout.write(self.style.SUCCESS('   - All 30 participants have submitted Workshop 1'))
        self.stdout.write(self.style.SUCCESS('   - Facilitator can now advance cohort to Workshop 2'))
        self.stdout.write(self.style.SUCCESS('   - Login as test_facilitator1 to test advancement\n'))