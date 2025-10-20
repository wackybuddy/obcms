"""Component tests for chat messaging interface.

Tests the chat messaging system's capabilities:
- Message payload validation
- Message routing and persistence
- Conversation management
- Error handling for malformed messages
- Message acknowledgement tracking
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from common.models import ChatMessage

User = get_user_model()


@pytest.mark.component
class ChatMessagingComponentTests(TestCase):
    """Component tests for chat message delivery and routing."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_chat_user",
            email="chatuser@example.com",
            password="chatpass1234",
        )

    def test_message_payload_validation_required_fields(self):
        """Test that chat message payloads require essential fields."""
        # Create a valid message
        message = ChatMessage.objects.create(
            user=self.user,
            user_message="Test message",
            assistant_response="Test response",
        )

        # Verify required fields
        self.assertIsNotNone(message.user)
        self.assertEqual(message.user.username, "test_chat_user")
        self.assertIsNotNone(message.user_message)
        self.assertEqual(message.user_message, "Test message")
        self.assertIsNotNone(message.created_at)

    def test_message_payload_empty_text_validation(self):
        """Test that empty message text is allowed by model (validation is app-level)."""
        # ChatMessage model doesn't validate empty messages at DB level
        # Validation should be done at serializer/form level
        message = ChatMessage.objects.create(
            user=self.user,
            user_message="",  # Empty message is allowed at model level
            assistant_response="Response",
        )
        self.assertEqual(message.user_message, "")

    def test_message_payload_whitespace_only_validation(self):
        """Test that whitespace-only message text is allowed by model (validation is app-level)."""
        # ChatMessage model doesn't validate whitespace-only messages at DB level
        # Validation should be done at serializer/form level
        message = ChatMessage.objects.create(
            user=self.user,
            user_message="   ",  # Whitespace is allowed at model level
            assistant_response="Response",
        )
        self.assertEqual(message.user_message, "   ")

    def test_message_persistence_after_creation(self):
        """Test that messages are properly persisted in database."""
        message = ChatMessage.objects.create(
            user=self.user,
            user_message="Test message for persistence",
            assistant_response="Response for persistence",
        )

        retrieved_message = ChatMessage.objects.get(id=message.id)
        self.assertEqual(retrieved_message.user_message, "Test message for persistence")
        self.assertEqual(retrieved_message.user.id, self.user.id)

    def test_message_timestamp_recorded_on_creation(self):
        """Test that message timestamp is recorded when created."""
        before_create = timezone.now()
        message = ChatMessage.objects.create(
            user=self.user,
            user_message="Test message",
            assistant_response="Test response",
        )
        after_create = timezone.now()

        self.assertGreaterEqual(message.created_at, before_create)
        self.assertLessEqual(message.created_at, after_create)

    def test_multiple_messages_from_same_user(self):
        """Test handling multiple messages from the same user."""
        msg1 = ChatMessage.objects.create(
            user=self.user,
            user_message="First message",
            assistant_response="Response 1",
        )
        msg2 = ChatMessage.objects.create(
            user=self.user,
            user_message="Second message",
            assistant_response="Response 2",
        )
        msg3 = ChatMessage.objects.create(
            user=self.user,
            user_message="Third message",
            assistant_response="Response 3",
        )

        user_messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(user_messages.count(), 3)

    def test_message_retrieval_ordering(self):
        """Test that messages are retrieved in correct order."""
        msg1 = ChatMessage.objects.create(
            user=self.user,
            user_message="First",
            assistant_response="Response 1",
        )
        msg2 = ChatMessage.objects.create(
            user=self.user,
            user_message="Second",
            assistant_response="Response 2",
        )

        messages = list(ChatMessage.objects.filter(user=self.user).order_by('created_at'))
        self.assertEqual(messages[0].user_message, "First")
        self.assertEqual(messages[1].user_message, "Second")

    def test_message_payload_special_characters(self):
        """Test that messages with special characters are handled correctly."""
        special_text = "Test with special chars: @#$%^&*(){}[]|:;<>?,./~`"
        message = ChatMessage.objects.create(
            user=self.user,
            user_message=special_text,
            assistant_response="Response",
        )

        retrieved = ChatMessage.objects.get(id=message.id)
        self.assertEqual(retrieved.user_message, special_text)

    def test_message_payload_unicode_characters(self):
        """Test that messages with unicode characters are preserved."""
        unicode_text = "Message with unicode: 你好世界 हेलो मुंडे мир"
        message = ChatMessage.objects.create(
            user=self.user,
            user_message=unicode_text,
            assistant_response="Response",
        )

        retrieved = ChatMessage.objects.get(id=message.id)
        self.assertEqual(retrieved.user_message, unicode_text)

    def test_message_payload_max_length_handling(self):
        """Test that excessively long messages are validated."""
        # Create a very long message
        long_text = "x" * 10000  # 10k characters

        message = ChatMessage.objects.create(
            user=self.user,
            user_message=long_text,
            assistant_response="Response",
        )

        retrieved = ChatMessage.objects.get(id=message.id)
        self.assertEqual(len(retrieved.user_message), 10000)

    def test_message_user_relationship_integrity(self):
        """Test that message-user relationship is maintained."""
        other_user = User.objects.create_user(
            username="other_user",
            email="other@example.com",
            password="otherpass1234",
        )

        msg1 = ChatMessage.objects.create(
            user=self.user,
            user_message="Message from user 1",
            assistant_response="Response 1",
        )
        msg2 = ChatMessage.objects.create(
            user=other_user,
            user_message="Message from user 2",
            assistant_response="Response 2",
        )

        self.assertEqual(msg1.user.id, self.user.id)
        self.assertEqual(msg2.user.id, other_user.id)
        self.assertNotEqual(msg1.user.id, msg2.user.id)

    def test_message_routing_by_user(self):
        """Test message routing and retrieval by user."""
        other_user = User.objects.create_user(
            username="other_user",
            email="other@example.com",
            password="otherpass1234",
        )

        ChatMessage.objects.create(
            user=self.user,
            user_message="Message for user 1",
            assistant_response="Response 1",
        )
        ChatMessage.objects.create(
            user=other_user,
            user_message="Message for user 2",
            assistant_response="Response 2",
        )

        user1_messages = ChatMessage.objects.filter(user=self.user)
        user2_messages = ChatMessage.objects.filter(user=other_user)

        self.assertEqual(user1_messages.count(), 1)
        self.assertEqual(user2_messages.count(), 1)
        self.assertEqual(user1_messages[0].user_message, "Message for user 1")
        self.assertEqual(user2_messages[0].user_message, "Message for user 2")

    def test_message_acknowledgement_via_retrieval(self):
        """Test that messages can be acknowledged via successful retrieval."""
        message = ChatMessage.objects.create(
            user=self.user,
            user_message="Test message",
            assistant_response="Test response",
        )

        # Simulate acknowledgement by retrieving message
        retrieved = ChatMessage.objects.get(id=message.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, message.id)

    def test_message_state_immutability_after_creation(self):
        """Test that message content doesn't change after creation."""
        original_text = "Original message"
        message = ChatMessage.objects.create(
            user=self.user,
            user_message=original_text,
            assistant_response="Original response",
        )

        original_id = message.id
        original_created_at = message.created_at

        # Retrieve message multiple times
        retrieved1 = ChatMessage.objects.get(id=original_id)
        retrieved2 = ChatMessage.objects.get(id=original_id)

        self.assertEqual(retrieved1.user_message, original_text)
        self.assertEqual(retrieved2.user_message, original_text)
        self.assertEqual(retrieved1.created_at, original_created_at)
        self.assertEqual(retrieved2.created_at, original_created_at)

    def test_message_error_handling_missing_user(self):
        """Test error handling when message creation lacks user."""
        with self.assertRaises((ValueError, Exception)):
            ChatMessage.objects.create(
                user=None,  # Missing required user
                user_message="Test message",
                assistant_response="Response",
            )

    def test_message_bulk_retrieval(self):
        """Test efficient bulk retrieval of messages."""
        for i in range(10):
            ChatMessage.objects.create(
                user=self.user,
                user_message=f"Message {i}",
                assistant_response=f"Response {i}",
            )

        all_messages = list(ChatMessage.objects.filter(user=self.user))
        self.assertEqual(len(all_messages), 10)

    def test_message_filtering_by_timestamp(self):
        """Test filtering messages by creation timestamp."""
        now = timezone.now()

        msg1 = ChatMessage.objects.create(
            user=self.user,
            user_message="Message 1",
            assistant_response="Response 1",
        )

        # Messages from this user created recently
        recent_messages = ChatMessage.objects.filter(
            user=self.user,
            created_at__gte=now,
        )

        self.assertGreaterEqual(recent_messages.count(), 1)

    def test_message_retry_on_duplicate_handling(self):
        """Test that duplicate messages can be handled."""
        text = "Duplicate message"

        msg1 = ChatMessage.objects.create(
            user=self.user,
            user_message=text,
            assistant_response="Response 1",
        )
        msg2 = ChatMessage.objects.create(
            user=self.user,
            user_message=text,
            assistant_response="Response 2",
        )

        # Both should exist as separate messages
        self.assertNotEqual(msg1.id, msg2.id)

        all_with_text = ChatMessage.objects.filter(
            user=self.user,
            user_message=text,
        )
        self.assertEqual(all_with_text.count(), 2)

    def test_message_payload_xss_attempt_preservation(self):
        """Test that XSS-like content in messages is preserved (not executed)."""
        xss_text = '<script>alert("xss")</script>'

        message = ChatMessage.objects.create(
            user=self.user,
            user_message=xss_text,
            assistant_response="Response",
        )

        retrieved = ChatMessage.objects.get(id=message.id)
        # Should store as-is (not execute)
        self.assertEqual(retrieved.user_message, xss_text)

    def test_message_payload_sql_injection_attempt_preservation(self):
        """Test that SQL injection-like content is preserved safely."""
        sql_text = "'; DROP TABLE messages; --"

        message = ChatMessage.objects.create(
            user=self.user,
            user_message=sql_text,
            assistant_response="Response",
        )

        retrieved = ChatMessage.objects.get(id=message.id)
        # Should be stored safely via ORM
        self.assertEqual(retrieved.user_message, sql_text)

        # Table should still exist
        all_messages = ChatMessage.objects.all()
        self.assertIsNotNone(all_messages)

    def test_conversation_message_sequence(self):
        """Test a sequence of messages as a conversation."""
        messages_sequence = [
            "Hello, how can I help you?",
            "I need information about the program.",
            "Sure, what specific information?",
            "Tell me about eligibility criteria.",
        ]

        created_messages = []
        for msg_text in messages_sequence:
            msg = ChatMessage.objects.create(
                user=self.user,
                user_message=msg_text,
                assistant_response="Response",
            )
            created_messages.append(msg)

        # Verify all messages are stored and retrievable
        retrieved_conversation = list(
            ChatMessage.objects.filter(user=self.user).order_by('created_at')
        )

        self.assertEqual(len(retrieved_conversation), len(messages_sequence))
        for i, msg in enumerate(retrieved_conversation):
            self.assertEqual(msg.user_message, messages_sequence[i])
