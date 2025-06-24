from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from policy_tracking.models import PolicyRecommendation
import uuid
import json

User = get_user_model()


class AIConversation(models.Model):
    """Model for storing AI assistant conversations."""
    
    CONVERSATION_TYPES = [
        ('policy_chat', 'Policy Chat'),
        ('document_generation', 'Document Generation'),
        ('analysis', 'Policy Analysis'),
        ('evidence_review', 'Evidence Review'),
        ('cultural_guidance', 'Cultural Guidance'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_conversations',
        help_text="User who initiated the conversation"
    )
    
    conversation_type = models.CharField(
        max_length=20,
        choices=CONVERSATION_TYPES,
        default='policy_chat',
        help_text="Type of AI conversation"
    )
    
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Conversation title (auto-generated or user-defined)"
    )
    
    # Related objects
    related_policy = models.ForeignKey(
        PolicyRecommendation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_conversations',
        help_text="Policy recommendation this conversation relates to"
    )
    
    # Conversation metadata
    messages = models.JSONField(
        default=list,
        help_text="Array of conversation messages with roles and content"
    )
    
    context_data = models.JSONField(
        default=dict,
        help_text="Additional context data for the conversation"
    )
    
    # AI model settings
    model_used = models.CharField(
        max_length=50,
        default='gemini-2.5-flash',
        help_text="AI model used for this conversation"
    )
    
    # Status and metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this conversation is active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'conversation_type']),
            models.Index(fields=['related_policy', 'is_active']),
            models.Index(fields=['created_at', 'user']),
        ]
    
    def __str__(self):
        date_str = self.created_at.strftime("%Y-%m-%d")
        return self.title or f'{self.conversation_type} - {date_str}'
    
    def add_message(self, role, content, metadata=None):
        """Add a message to the conversation."""
        message = {
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'timestamp': timezone.now().isoformat(),
            'metadata': metadata or {}
        }
        self.messages.append(message)
        self.save(update_fields=['messages', 'updated_at'])
    
    @property
    def message_count(self):
        """Get the number of messages in this conversation."""
        return len(self.messages)
    
    @property
    def last_message_time(self):
        """Get the timestamp of the last message."""
        if self.messages:
            return self.messages[-1].get('timestamp')
        return None


class AIInsight(models.Model):
    """Model for storing AI-generated insights about policies and communities."""
    
    INSIGHT_TYPES = [
        ('policy_analysis', 'Policy Analysis'),
        ('impact_prediction', 'Impact Prediction'),
        ('stakeholder_analysis', 'Stakeholder Analysis'),
        ('cultural_considerations', 'Cultural Considerations'),
        ('implementation_guidance', 'Implementation Guidance'),
        ('evidence_synthesis', 'Evidence Synthesis'),
        ('risk_assessment', 'Risk Assessment'),
        ('opportunity_identification', 'Opportunity Identification'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('high', 'High Confidence'),
        ('medium', 'Medium Confidence'),
        ('low', 'Low Confidence'),
        ('experimental', 'Experimental'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    title = models.CharField(
        max_length=255,
        help_text="Title of the insight"
    )
    
    insight_type = models.CharField(
        max_length=30,
        choices=INSIGHT_TYPES,
        help_text="Type of insight generated"
    )
    
    content = models.TextField(
        help_text="Detailed content of the AI insight"
    )
    
    summary = models.TextField(
        blank=True,
        help_text="Brief summary of the insight"
    )
    
    # Relationships
    related_policy = models.ForeignKey(
        PolicyRecommendation,
        on_delete=models.CASCADE,
        related_name='ai_insights',
        help_text="Policy recommendation this insight relates to"
    )
    
    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='insights',
        help_text="Conversation that generated this insight"
    )
    
    # AI metadata
    model_used = models.CharField(
        max_length=50,
        default='gemini-2.5-flash',
        help_text="AI model used to generate this insight"
    )
    
    confidence_level = models.CharField(
        max_length=15,
        choices=CONFIDENCE_LEVELS,
        default='medium',
        help_text="Confidence level of the AI insight"
    )
    
    # Structured data
    key_points = models.JSONField(
        default=list,
        help_text="Key points extracted from the insight"
    )
    
    recommendations = models.JSONField(
        default=list,
        help_text="Specific recommendations from the insight"
    )
    
    cultural_considerations = models.JSONField(
        default=list,
        help_text="Cultural considerations for Bangsamoro communities"
    )
    
    # Validation and review
    is_validated = models.BooleanField(
        default=False,
        help_text="Whether this insight has been validated by human experts"
    )
    
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_insights',
        help_text="User who validated this insight"
    )
    
    validation_notes = models.TextField(
        blank=True,
        help_text="Notes from human validation"
    )
    
    # Usage tracking
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this insight has been viewed"
    )
    
    usefulness_score = models.FloatField(
        null=True,
        blank=True,
        help_text="User-rated usefulness score (0-5)"
    )
    
    # Metadata
    generated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='generated_insights',
        help_text="User who generated this insight"
    )
    
    tags = models.JSONField(
        default=list,
        help_text="Tags for categorizing and searching insights"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['related_policy', 'insight_type']),
            models.Index(fields=['is_validated', 'confidence_level']),
            models.Index(fields=['created_at', 'insight_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.insight_type}"
    
    def increment_view_count(self):
        """Increment the view count for this insight."""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class AIGeneratedDocument(models.Model):
    """Model for storing AI-generated documents like policy briefs and reports."""
    
    DOCUMENT_TYPES = [
        ('policy_brief', 'Policy Brief'),
        ('executive_summary', 'Executive Summary'),
        ('implementation_plan', 'Implementation Plan'),
        ('impact_assessment', 'Impact Assessment'),
        ('stakeholder_report', 'Stakeholder Report'),
        ('cultural_analysis', 'Cultural Analysis'),
        ('evidence_report', 'Evidence Report'),
        ('recommendation_memo', 'Recommendation Memo'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    title = models.CharField(
        max_length=255,
        help_text="Title of the generated document"
    )
    
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        help_text="Type of document generated"
    )
    
    content = models.TextField(
        help_text="Generated document content"
    )
    
    # Relationships
    related_policy = models.ForeignKey(
        PolicyRecommendation,
        on_delete=models.CASCADE,
        related_name='ai_generated_documents',
        help_text="Policy recommendation this document relates to"
    )
    
    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_documents',
        help_text="Conversation that generated this document"
    )
    
    # Generation metadata
    prompt_used = models.TextField(
        help_text="Prompt used to generate this document"
    )
    
    model_used = models.CharField(
        max_length=50,
        default='gemini-2.5-flash',
        help_text="AI model used to generate this document"
    )
    
    generation_parameters = models.JSONField(
        default=dict,
        help_text="Parameters used for document generation"
    )
    
    # Document structure
    sections = models.JSONField(
        default=list,
        help_text="Document sections with titles and content"
    )
    
    key_points = models.JSONField(
        default=list,
        help_text="Key points extracted from the document"
    )
    
    # Review and approval
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Document status"
    )
    
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_ai_documents',
        help_text="User who reviewed this document"
    )
    
    review_notes = models.TextField(
        blank=True,
        help_text="Review comments and feedback"
    )
    
    # Export formats
    pdf_file = models.FileField(
        upload_to='ai_documents/pdf/%Y/%m/',
        null=True,
        blank=True,
        help_text="Generated PDF version"
    )
    
    word_file = models.FileField(
        upload_to='ai_documents/word/%Y/%m/',
        null=True,
        blank=True,
        help_text="Generated Word document version"
    )
    
    # Metadata
    generated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='generated_documents',
        help_text="User who generated this document"
    )
    
    download_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this document has been downloaded"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['related_policy', 'document_type']),
            models.Index(fields=['status', 'document_type']),
            models.Index(fields=['created_at', 'generated_by']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.document_type}"
    
    def increment_download_count(self):
        """Increment the download count for this document."""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class AIUsageMetrics(models.Model):
    """Model for tracking AI usage metrics and analytics."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_usage_metrics'
    )
    
    date = models.DateField(default=timezone.now)
    
    # Usage counts
    conversations_started = models.PositiveIntegerField(default=0)
    messages_sent = models.PositiveIntegerField(default=0)
    insights_generated = models.PositiveIntegerField(default=0)
    documents_created = models.PositiveIntegerField(default=0)
    
    # Feature usage
    policy_analysis_used = models.PositiveIntegerField(default=0)
    document_generation_used = models.PositiveIntegerField(default=0)
    cultural_guidance_used = models.PositiveIntegerField(default=0)
    evidence_review_used = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    average_response_time = models.FloatField(null=True, blank=True)
    total_tokens_used = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date', 'user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"AI Usage - {self.user.username} - {self.date}"
