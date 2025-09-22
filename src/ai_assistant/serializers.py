from django.contrib.auth import get_user_model
from rest_framework import serializers

from recommendations.policy_tracking.models import PolicyRecommendation

from .models import (AIConversation, AIGeneratedDocument, AIInsight,
                     AIUsageMetrics)

User = get_user_model()


class AIConversationSerializer(serializers.ModelSerializer):
    """Serializer for AI conversations."""

    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    related_policy_title = serializers.CharField(
        source="related_policy.title", read_only=True
    )
    message_count = serializers.IntegerField(read_only=True)
    last_message_time = serializers.CharField(read_only=True)

    class Meta:
        model = AIConversation
        fields = [
            "id",
            "user",
            "user_name",
            "conversation_type",
            "title",
            "related_policy",
            "related_policy_title",
            "messages",
            "context_data",
            "model_used",
            "is_active",
            "message_count",
            "last_message_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user"]


class AIConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating AI conversations."""

    class Meta:
        model = AIConversation
        fields = ["conversation_type", "title", "related_policy", "context_data"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ChatMessageSerializer(serializers.Serializer):
    """Serializer for chat messages."""

    message = serializers.CharField(max_length=5000)
    conversation_id = serializers.UUIDField(required=False)
    conversation_type = serializers.ChoiceField(
        choices=AIConversation.CONVERSATION_TYPES, default="policy_chat"
    )
    related_policy = serializers.UUIDField(required=False)

    def validate_related_policy(self, value):
        if value:
            try:
                PolicyRecommendation.objects.get(id=value)
            except PolicyRecommendation.DoesNotExist:
                raise serializers.ValidationError("Policy recommendation not found.")
        return value


class AIInsightSerializer(serializers.ModelSerializer):
    """Serializer for AI insights."""

    generated_by_name = serializers.CharField(
        source="generated_by.get_full_name", read_only=True
    )
    validated_by_name = serializers.CharField(
        source="validated_by.get_full_name", read_only=True
    )
    related_policy_title = serializers.CharField(
        source="related_policy.title", read_only=True
    )

    class Meta:
        model = AIInsight
        fields = [
            "id",
            "title",
            "insight_type",
            "content",
            "summary",
            "related_policy",
            "related_policy_title",
            "conversation",
            "model_used",
            "confidence_level",
            "key_points",
            "recommendations",
            "cultural_considerations",
            "is_validated",
            "validated_by",
            "validated_by_name",
            "validation_notes",
            "view_count",
            "usefulness_score",
            "generated_by",
            "generated_by_name",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "view_count",
            "generated_by",
            "created_at",
            "updated_at",
        ]


class AIGeneratedDocumentSerializer(serializers.ModelSerializer):
    """Serializer for AI generated documents."""

    generated_by_name = serializers.CharField(
        source="generated_by.get_full_name", read_only=True
    )
    reviewed_by_name = serializers.CharField(
        source="reviewed_by.get_full_name", read_only=True
    )
    related_policy_title = serializers.CharField(
        source="related_policy.title", read_only=True
    )

    class Meta:
        model = AIGeneratedDocument
        fields = [
            "id",
            "title",
            "document_type",
            "content",
            "related_policy",
            "related_policy_title",
            "conversation",
            "prompt_used",
            "model_used",
            "generation_parameters",
            "sections",
            "key_points",
            "status",
            "reviewed_by",
            "reviewed_by_name",
            "review_notes",
            "pdf_file",
            "word_file",
            "generated_by",
            "generated_by_name",
            "download_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "download_count",
            "generated_by",
            "created_at",
            "updated_at",
        ]


class DocumentGenerationRequestSerializer(serializers.Serializer):
    """Serializer for document generation requests."""

    document_type = serializers.ChoiceField(choices=AIGeneratedDocument.DOCUMENT_TYPES)
    policy_id = serializers.UUIDField()
    title = serializers.CharField(max_length=255, required=False)
    additional_context = serializers.JSONField(required=False)

    def validate_policy_id(self, value):
        try:
            PolicyRecommendation.objects.get(id=value)
        except PolicyRecommendation.DoesNotExist:
            raise serializers.ValidationError("Policy recommendation not found.")
        return value


class AIInsightCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating AI insights."""

    class Meta:
        model = AIInsight
        fields = [
            "title",
            "insight_type",
            "content",
            "summary",
            "related_policy",
            "conversation",
            "confidence_level",
            "key_points",
            "recommendations",
            "cultural_considerations",
            "tags",
        ]

    def create(self, validated_data):
        validated_data["generated_by"] = self.context["request"].user
        return super().create(validated_data)


class AIUsageMetricsSerializer(serializers.ModelSerializer):
    """Serializer for AI usage metrics."""

    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = AIUsageMetrics
        fields = [
            "user",
            "user_name",
            "date",
            "conversations_started",
            "messages_sent",
            "insights_generated",
            "documents_created",
            "policy_analysis_used",
            "document_generation_used",
            "cultural_guidance_used",
            "evidence_review_used",
            "average_response_time",
            "total_tokens_used",
            "created_at",
        ]
        read_only_fields = ["user", "created_at"]


class PolicyAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for policy analysis requests."""

    policy_id = serializers.UUIDField()
    analysis_type = serializers.ChoiceField(
        choices=[
            ("comprehensive", "Comprehensive Analysis"),
            ("impact_assessment", "Impact Assessment"),
            ("stakeholder_analysis", "Stakeholder Analysis"),
            ("cultural_assessment", "Cultural Assessment"),
            ("implementation_analysis", "Implementation Analysis"),
            ("risk_assessment", "Risk Assessment"),
        ]
    )
    focus_areas = serializers.ListField(
        child=serializers.CharField(max_length=100), required=False
    )
    additional_context = serializers.JSONField(required=False)

    def validate_policy_id(self, value):
        try:
            PolicyRecommendation.objects.get(id=value)
        except PolicyRecommendation.DoesNotExist:
            raise serializers.ValidationError("Policy recommendation not found.")
        return value


class EvidenceReviewRequestSerializer(serializers.Serializer):
    """Serializer for evidence review requests."""

    policy_id = serializers.UUIDField()
    evidence_documents = serializers.ListField(
        child=serializers.CharField(max_length=500), required=False
    )
    review_focus = serializers.ChoiceField(
        choices=[
            ("quality_assessment", "Quality Assessment"),
            ("gap_analysis", "Gap Analysis"),
            ("synthesis", "Evidence Synthesis"),
            ("validation", "Evidence Validation"),
        ],
        default="quality_assessment",
    )

    def validate_policy_id(self, value):
        try:
            PolicyRecommendation.objects.get(id=value)
        except PolicyRecommendation.DoesNotExist:
            raise serializers.ValidationError("Policy recommendation not found.")
        return value


class CulturalGuidanceRequestSerializer(serializers.Serializer):
    """Serializer for cultural guidance requests."""

    policy_id = serializers.UUIDField()
    guidance_type = serializers.ChoiceField(
        choices=[
            ("appropriateness_review", "Cultural Appropriateness Review"),
            ("implementation_guidance", "Implementation Guidance"),
            ("stakeholder_engagement", "Stakeholder Engagement Strategy"),
            ("risk_mitigation", "Cultural Risk Mitigation"),
            ("communication_strategy", "Communication Strategy"),
        ]
    )
    specific_concerns = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    target_communities = serializers.ListField(
        child=serializers.CharField(max_length=100), required=False
    )

    def validate_policy_id(self, value):
        try:
            PolicyRecommendation.objects.get(id=value)
        except PolicyRecommendation.DoesNotExist:
            raise serializers.ValidationError("Policy recommendation not found.")
        return value


class AIResponseSerializer(serializers.Serializer):
    """Serializer for AI responses."""

    success = serializers.BooleanField()
    response = serializers.CharField()
    model_used = serializers.CharField()
    response_time = serializers.FloatField()
    timestamp = serializers.CharField()
    conversation_type = serializers.CharField(required=False)
    metadata = serializers.JSONField(required=False)
    insights = serializers.ListField(required=False)
    error = serializers.CharField(required=False)

    # Additional fields for document generation
    document_structure = serializers.JSONField(required=False)


class ConversationHistorySerializer(serializers.Serializer):
    """Serializer for conversation history."""

    role = serializers.CharField()
    content = serializers.CharField()
    timestamp = serializers.CharField()
    metadata = serializers.JSONField(required=False)
