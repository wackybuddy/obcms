from rest_framework import serializers
from .models import PolicyRecommendation, PolicyEvidence, PolicyImpact, PolicyDocument


class PolicyEvidenceSerializer(serializers.ModelSerializer):
    """Serializer for PolicyEvidence model."""
    recommendation_title = serializers.CharField(source='recommendation.title', read_only=True)
    evidence_type_display = serializers.CharField(source='get_evidence_type_display', read_only=True)
    
    class Meta:
        model = PolicyEvidence
        fields = '__all__'


class PolicyImpactSerializer(serializers.ModelSerializer):
    """Serializer for PolicyImpact model."""
    recommendation_title = serializers.CharField(source='recommendation.title', read_only=True)
    
    class Meta:
        model = PolicyImpact
        fields = '__all__'


class PolicyDocumentSerializer(serializers.ModelSerializer):
    """Serializer for PolicyDocument model."""
    recommendation_title = serializers.CharField(source='recommendation.title', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = PolicyDocument
        fields = '__all__'


class PolicyRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for PolicyRecommendation model."""
    related_need_title = serializers.CharField(source='related_need.title', read_only=True)
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    policy_category_display = serializers.CharField(source='get_policy_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_level_display = serializers.CharField(source='get_priority_level_display', read_only=True)
    evidence = PolicyEvidenceSerializer(many=True, read_only=True)
    impacts = PolicyImpactSerializer(many=True, read_only=True)
    documents = PolicyDocumentSerializer(many=True, read_only=True)
    evidence_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PolicyRecommendation
        fields = '__all__'
        
    def get_evidence_count(self, obj):
        return obj.evidence.count()


class PolicyRecommendationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for PolicyRecommendation list view."""
    related_need_title = serializers.CharField(source='related_need.title', read_only=True)
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    policy_category_display = serializers.CharField(source='get_policy_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_level_display = serializers.CharField(source='get_priority_level_display', read_only=True)
    evidence_count = serializers.SerializerMethodField()
    impact_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PolicyRecommendation
        fields = [
            'id', 'reference_number', 'title', 'policy_category', 'policy_category_display',
            'status', 'status_display', 'priority_level', 'priority_level_display',
            'related_need_title', 'submitted_by_name', 'submission_date',
            'target_implementation_date', 'evidence_count', 'impact_count', 'created_at'
        ]
        
    def get_evidence_count(self, obj):
        return obj.evidence.count()
        
    def get_impact_count(self, obj):
        return obj.impacts.count()


class PolicyEvidenceListSerializer(serializers.ModelSerializer):
    """Simplified serializer for PolicyEvidence list view."""
    recommendation_title = serializers.CharField(source='recommendation.title', read_only=True)
    evidence_type_display = serializers.CharField(source='get_evidence_type_display', read_only=True)
    
    class Meta:
        model = PolicyEvidence
        fields = [
            'id', 'recommendation_title', 'evidence_type', 'evidence_type_display',
            'title', 'source', 'reliability_score', 'is_verified', 'verification_date'
        ]


class PolicyImpactListSerializer(serializers.ModelSerializer):
    """Simplified serializer for PolicyImpact list view."""
    recommendation_title = serializers.CharField(source='recommendation.title', read_only=True)
    
    class Meta:
        model = PolicyImpact
        fields = [
            'id', 'recommendation_title', 'indicator_name', 'baseline_value',
            'target_value', 'actual_value', 'measurement_date', 'impact_assessment'
        ]


class PolicyDocumentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for PolicyDocument list view."""
    recommendation_title = serializers.CharField(source='recommendation.title', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = PolicyDocument
        fields = [
            'id', 'recommendation_title', 'document_type', 'document_type_display',
            'title', 'version', 'upload_date', 'file_size', 'is_public'
        ]