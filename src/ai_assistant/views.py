from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
from django.core.cache import cache

from .models import AIConversation, AIInsight, AIGeneratedDocument, AIUsageMetrics
from .serializers import (
    AIConversationSerializer, AIConversationCreateSerializer, ChatMessageSerializer,
    AIInsightSerializer, AIInsightCreateSerializer, AIGeneratedDocumentSerializer,
    DocumentGenerationRequestSerializer, PolicyAnalysisRequestSerializer,
    EvidenceReviewRequestSerializer, CulturalGuidanceRequestSerializer,
    AIResponseSerializer, AIUsageMetricsSerializer
)
from .ai_engine import GeminiAIEngine
from policy_tracking.models import PolicyRecommendation
from policy_tracking.serializers import PolicyRecommendationSerializer

import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatAPIView(APIView):
    """Direct chat API for quick AI interactions."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Send a message to AI assistant."""
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = serializer.validated_data['message']
        conversation_id = serializer.validated_data.get('conversation_id')
        conversation_type = serializer.validated_data.get('conversation_type', 'policy_chat')
        related_policy_id = serializer.validated_data.get('related_policy')
        
        # Get or create conversation
        conversation = None
        if conversation_id:
            try:
                conversation = AIConversation.objects.get(
                    id=conversation_id, 
                    user=request.user,
                    is_active=True
                )
            except AIConversation.DoesNotExist:
                pass
        
        if not conversation:
            # Create new conversation
            conversation_data = {
                'user': request.user,
                'conversation_type': conversation_type,
                'title': message[:100] + '...' if len(message) > 100 else message
            }
            
            if related_policy_id:
                try:
                    policy = PolicyRecommendation.objects.get(id=related_policy_id)
                    conversation_data['related_policy'] = policy
                except PolicyRecommendation.DoesNotExist:
                    pass
            
            conversation = AIConversation.objects.create(**conversation_data)
            self._update_usage_metrics(request.user, 'conversations_started')
        
        # Add user message
        conversation.add_message('user', message)
        
        # Generate AI response
        ai_engine = GeminiAIEngine()
        
        # Prepare context
        context_data = {}
        if conversation.related_policy:
            context_data['policy'] = {
                'title': conversation.related_policy.title,
                'category': conversation.related_policy.category,
                'status': conversation.related_policy.status,
                'description': conversation.related_policy.description,
                'problem_statement': conversation.related_policy.problem_statement,
                'proposed_solution': conversation.related_policy.proposed_solution,
                'expected_outcomes': conversation.related_policy.expected_outcomes,
            }
        
        ai_response = ai_engine.generate_response(
            prompt=message,
            conversation_type=conversation_type,
            context_data=context_data,
            conversation_history=conversation.messages[-10:]  # Last 10 messages
        )
        
        if ai_response['success']:
            conversation.add_message('assistant', ai_response['response'])
            self._update_usage_metrics(request.user, 'messages_sent')
        
        # Add conversation ID to response
        ai_response['conversation_id'] = str(conversation.id)
        
        return Response(AIResponseSerializer(ai_response).data)
    
    def _update_usage_metrics(self, user, metric_type):
        """Update user's AI usage metrics."""
        today = timezone.now().date()
        metrics, created = AIUsageMetrics.objects.get_or_create(
            user=user, 
            date=today,
            defaults={metric_type: 1}
        )
        if not created:
            setattr(metrics, metric_type, getattr(metrics, metric_type) + 1)
            metrics.save()


class DocumentGenerationAPIView(APIView):
    """API for AI document generation."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Generate a document using AI."""
        serializer = DocumentGenerationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        document_type = serializer.validated_data['document_type']
        policy_id = serializer.validated_data['policy_id']
        title = serializer.validated_data.get('title')
        additional_context = serializer.validated_data.get('additional_context', {})
        
        # Get policy
        policy = get_object_or_404(PolicyRecommendation, id=policy_id)
        
        # Generate document
        ai_engine = GeminiAIEngine()
        policy_data = {
            'title': policy.title,
            'category': policy.category,
            'status': policy.status,
            'priority': policy.priority,
            'description': policy.description,
            'problem_statement': policy.problem_statement,
            'proposed_solution': policy.proposed_solution,
            'expected_outcomes': policy.expected_outcomes,
        }
        
        ai_response = ai_engine.generate_document(
            document_type=document_type,
            policy_data=policy_data,
            additional_context=additional_context
        )
        
        if ai_response['success']:
            # Create document record
            document_title = title or f"{document_type.replace('_', ' ').title()} - {policy.title}"
            
            document = AIGeneratedDocument.objects.create(
                title=document_title,
                document_type=document_type,
                content=ai_response['response'],
                related_policy=policy,
                prompt_used=f"Generate {document_type} for policy: {policy.title}",
                sections=ai_response.get('document_structure', {}).get('sections', []),
                key_points=ai_response.get('document_structure', {}).get('key_points', []),
                generated_by=request.user
            )
            
            ai_response['document_id'] = str(document.id)
            
            # Track usage
            self._update_usage_metrics(request.user, 'document_generation_used')
            self._update_usage_metrics(request.user, 'documents_created')
        
        return Response(AIResponseSerializer(ai_response).data)
    
    def _update_usage_metrics(self, user, metric_type):
        """Update user's AI usage metrics."""
        today = timezone.now().date()
        metrics, created = AIUsageMetrics.objects.get_or_create(
            user=user, 
            date=today,
            defaults={metric_type: 1}
        )
        if not created:
            setattr(metrics, metric_type, getattr(metrics, metric_type) + 1)
            metrics.save()
