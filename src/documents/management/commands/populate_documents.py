from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from documents.models import DocumentCategory, Document, DocumentAccess, DocumentComment
import random
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with sample document data for OBC Management System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing document data before populating'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing document data...')
            Document.objects.all().delete()
            DocumentCategory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing document data'))

        self.stdout.write('Creating document categories...')
        self.create_categories()
        
        self.stdout.write('Creating sample documents...')
        self.create_documents()
        
        self.stdout.write('Creating document access records...')
        self.create_access_records()
        
        self.stdout.write('Creating document comments...')
        self.create_comments()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated document data'))

    def create_categories(self):
        """Create document categories relevant to OBC management."""
        categories = [
            {
                'name': 'Legal Documents',
                'description': 'Legal documents, ordinances, and regulatory materials',
                'color': '#1f77b4'
            },
            {
                'name': 'Community Reports',
                'description': 'Community assessment reports and documentation',
                'color': '#ff7f0e'
            },
            {
                'name': 'Cultural Preservation',
                'description': 'Documents related to cultural heritage and preservation',
                'color': '#2ca02c'
            },
            {
                'name': 'Administrative Records',
                'description': 'Administrative policies, procedures, and records',
                'color': '#d62728'
            },
            {
                'name': 'Project Documentation',
                'description': 'Project plans, reports, and implementation documents',
                'color': '#9467bd'
            },
            {
                'name': 'Research Studies',
                'description': 'Academic research and studies on Bangsamoro communities',
                'color': '#8c564b'
            },
            {
                'name': 'Meeting Minutes',
                'description': 'Minutes from various meetings and assemblies',
                'color': '#e377c2'
            },
            {
                'name': 'Budget and Finance',
                'description': 'Financial reports, budgets, and funding documents',
                'color': '#7f7f7f'
            },
            {
                'name': 'Training Materials',
                'description': 'Educational and training resources',
                'color': '#bcbd22'
            },
            {
                'name': 'Partnership Agreements',
                'description': 'MOUs, MOAs, and partnership documentation',
                'color': '#17becf'
            }
        ]

        for cat_data in categories:
            category, created = DocumentCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'color': cat_data['color']
                }
            )
            if created:
                self.stdout.write(f'  Created category: {category.name}')

    def create_documents(self):
        """Create sample documents for the system."""
        categories = list(DocumentCategory.objects.all())
        users = list(User.objects.all())
        
        if not users:
            self.stdout.write(self.style.WARNING('No users found. Please create users first.'))
            return

        documents = [
            # Legal Documents
            {
                'title': 'Bangsamoro Organic Law Implementation Guidelines',
                'description': 'Comprehensive guidelines for implementing BOL in Other Bangsamoro Communities',
                'category': 'Legal Documents',
                'confidentiality_level': 'public',
                'tags': 'BOL,implementation,guidelines,legal',
                'file_type': 'pdf'
            },
            {
                'title': 'OBC Registration Procedures Manual',
                'description': 'Step-by-step procedures for registering Other Bangsamoro Communities',
                'category': 'Legal Documents',
                'confidentiality_level': 'internal',
                'tags': 'registration,procedures,manual',
                'file_type': 'docx'
            },
            {
                'title': 'Land Rights Documentation Framework',
                'description': 'Framework for documenting and protecting OBC land rights',
                'category': 'Legal Documents',
                'confidentiality_level': 'restricted',
                'tags': 'land_rights,framework,protection',
                'file_type': 'pdf'
            },
            
            # Community Reports
            {
                'title': 'Zamboanga OBC Communities Assessment Report 2024',
                'description': 'Comprehensive assessment of OBC communities in Zamboanga Peninsula',
                'category': 'Community Reports',
                'confidentiality_level': 'internal',
                'tags': 'zamboanga,assessment,2024,communities',
                'file_type': 'pdf'
            },
            {
                'title': 'Sultan Kudarat Indigenous Practices Documentation',
                'description': 'Documentation of traditional practices in Sultan Kudarat OBC communities',
                'category': 'Community Reports',
                'confidentiality_level': 'public',
                'tags': 'sultan_kudarat,practices,documentation',
                'file_type': 'docx'
            },
            {
                'title': 'North Cotabato Community Needs Analysis',
                'description': 'Analysis of development needs in North Cotabato OBC communities',
                'category': 'Community Reports',
                'confidentiality_level': 'internal',
                'tags': 'north_cotabato,needs_analysis,development',
                'file_type': 'xlsx'
            },
            
            # Cultural Preservation
            {
                'title': 'Maranao Cultural Heritage Preservation Plan',
                'description': 'Strategic plan for preserving Maranao cultural heritage in OBC areas',
                'category': 'Cultural Preservation',
                'confidentiality_level': 'public',
                'tags': 'maranao,heritage,preservation,plan',
                'file_type': 'pdf'
            },
            {
                'title': 'Traditional Governance Systems Study',
                'description': 'Study on traditional governance systems in Bangsamoro communities',
                'category': 'Cultural Preservation',
                'confidentiality_level': 'public',
                'tags': 'governance,traditional,study',
                'file_type': 'pdf'
            },
            {
                'title': 'Language Preservation Initiative Documentation',
                'description': 'Documentation of efforts to preserve Bangsamoro languages',
                'category': 'Cultural Preservation',
                'confidentiality_level': 'public',
                'tags': 'language,preservation,initiative',
                'file_type': 'docx'
            },
            
            # Administrative Records
            {
                'title': 'OBC Administrative Structure Manual',
                'description': 'Manual outlining the administrative structure for OBC management',
                'category': 'Administrative Records',
                'confidentiality_level': 'internal',
                'tags': 'administrative,structure,manual',
                'file_type': 'pdf'
            },
            {
                'title': 'Personnel Management Guidelines',
                'description': 'Guidelines for managing personnel in OBC offices',
                'category': 'Administrative Records',
                'confidentiality_level': 'confidential',
                'tags': 'personnel,management,guidelines',
                'file_type': 'docx'
            },
            {
                'title': 'Emergency Response Procedures',
                'description': 'Emergency response procedures for OBC communities',
                'category': 'Administrative Records',
                'confidentiality_level': 'internal',
                'tags': 'emergency,response,procedures',
                'file_type': 'pdf'
            },
            
            # Project Documentation
            {
                'title': 'Livelihood Development Project Proposal',
                'description': 'Proposal for livelihood development projects in OBC communities',
                'category': 'Project Documentation',
                'confidentiality_level': 'internal',
                'tags': 'livelihood,development,proposal',
                'file_type': 'docx'
            },
            {
                'title': 'Infrastructure Development Master Plan',
                'description': 'Master plan for infrastructure development in OBC areas',
                'category': 'Project Documentation',
                'confidentiality_level': 'restricted',
                'tags': 'infrastructure,development,master_plan',
                'file_type': 'pdf'
            },
            {
                'title': 'Education Enhancement Program Design',
                'description': 'Program design for enhancing education in OBC communities',
                'category': 'Project Documentation',
                'confidentiality_level': 'internal',
                'tags': 'education,enhancement,program',
                'file_type': 'pptx'
            },
        ]

        for doc_data in documents:
            try:
                category = DocumentCategory.objects.get(name=doc_data['category'])
                user = random.choice(users)
                
                # Create sample file content
                file_content = self.create_sample_file_content(doc_data['title'], doc_data['file_type'])
                filename = f"{doc_data['title'].replace(' ', '_').lower()}.{doc_data['file_type']}"
                
                document = Document.objects.create(
                    title=doc_data['title'],
                    description=doc_data['description'],
                    category=category,
                    uploaded_by=user,
                    confidentiality_level=doc_data['confidentiality_level'],
                    tags=doc_data['tags'],
                    file=ContentFile(file_content, name=filename),
                    download_count=random.randint(0, 50)
                )
                
                # Set random created date within last 6 months
                days_ago = random.randint(1, 180)
                document.created_at = datetime.now() - timedelta(days=days_ago)
                document.updated_at = document.created_at + timedelta(days=random.randint(0, days_ago))
                document.save()
                
                self.stdout.write(f'  Created document: {document.title}')
                
            except DocumentCategory.DoesNotExist:
                self.stdout.write(f'  Warning: Category "{doc_data["category"]}" not found')
            except Exception as e:
                self.stdout.write(f'  Error creating document "{doc_data["title"]}": {str(e)}')

    def create_sample_file_content(self, title, file_type):
        """Create sample file content based on file type."""
        if file_type == 'pdf':
            return f"PDF Document: {title}\n\nThis is a sample PDF document for the OBC Management System.\n\nContent includes relevant information about {title.lower()}."
        elif file_type == 'docx':
            return f"Word Document: {title}\n\nThis is a sample Word document.\n\nDetailed content about {title.lower()} would be included here."
        elif file_type == 'xlsx':
            return f"Excel Spreadsheet: {title}\n\nThis would contain spreadsheet data related to {title.lower()}."
        elif file_type == 'pptx':
            return f"PowerPoint Presentation: {title}\n\nThis would be a presentation about {title.lower()}."
        else:
            return f"Document: {title}\n\nSample content for {title.lower()}."

    def create_access_records(self):
        """Create sample document access records."""
        documents = list(Document.objects.all())
        users = list(User.objects.all())
        
        if not documents or not users:
            return
        
        # Create some access records
        for _ in range(50):
            document = random.choice(documents)
            user = random.choice(users)
            
            # Skip if access record already exists or user is document owner
            if DocumentAccess.objects.filter(document=document, user=user).exists() or document.uploaded_by == user:
                continue
            
            access_type = random.choice(['view', 'download', 'upload'])
            
            # Create access record
            days_ago = random.randint(1, 90)
            access_date = datetime.now() - timedelta(days=days_ago)
            
            DocumentAccess.objects.create(
                document=document,
                user=user,
                access_type=access_type,
                granted_by=document.uploaded_by,
                ip_address=f'192.168.1.{random.randint(1, 254)}',
                user_agent='Sample User Agent',
                accessed_at=access_date,
                is_active=random.choice([True, True, True, False])  # Mostly active
            )

    def create_comments(self):
        """Create sample document comments."""
        documents = list(Document.objects.filter(confidentiality_level__in=['public', 'internal']))
        users = list(User.objects.all())
        
        if not documents or not users:
            return
        
        comments = [
            "This document provides excellent guidance for our implementation efforts.",
            "Could we get an updated version of this document?",
            "Very comprehensive coverage of the topic.",
            "This should be shared with all community leaders.",
            "The framework outlined here is very practical.",
            "Need to review section 3 for accuracy.",
            "Great resource for training materials.",
            "This aligns well with our current policies.",
            "Suggest adding more examples in the next version.",
            "Useful reference for field workers."
        ]
        
        # Create comments for random documents
        for _ in range(30):
            document = random.choice(documents)
            user = random.choice(users)
            comment_text = random.choice(comments)
            
            days_ago = random.randint(1, 60)
            comment_date = datetime.now() - timedelta(days=days_ago)
            
            comment = DocumentComment.objects.create(
                document=document,
                author=user,
                content=comment_text
            )
            
            # Set random created date
            comment.created_at = comment_date
            comment.save()