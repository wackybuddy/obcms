"""Component tests for security alerting messaging interface.

Tests the alerting system's messaging capabilities:
- Slack webhook delivery
- Email alert delivery
- Alert payload construction
- Error handling for failed alerts
- Severity level routing
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from common.alerting import (
    send_security_alert,
    send_slack_alert,
    send_email_alert,
    alert_brute_force_attack,
    alert_account_lockout,
    alert_suspicious_api_activity,
    alert_mass_data_export,
    alert_unauthorized_access,
    alert_admin_action,
    check_alerting_configuration,
)

User = get_user_model()


@pytest.mark.component
class AlertingMessagingComponentTests(TestCase):
    """Component tests for alert message delivery."""

    def setUp(self):
        self.test_user = User.objects.create_user(
            username="test_user",
            email="testuser@example.com",
            password="testpass1234",
        )
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass1234",
        )

    def test_alert_payload_construction_info_level(self):
        """Test that INFO severity alert payload is constructed correctly."""
        with patch("common.alerting._log_alert") as mock_log:
            send_security_alert(
                event_type="Test Event",
                details="Test details",
                severity="INFO",
            )
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            self.assertEqual(call_args[0][0], "INFO")
            self.assertEqual(call_args[0][1], "Test Event")

    def test_alert_payload_construction_warning_level(self):
        """Test that WARNING severity alert payload is constructed correctly."""
        with patch("common.alerting._log_alert") as mock_log:
            send_security_alert(
                event_type="Warning Event",
                details="Warning details",
                severity="WARNING",
            )
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            self.assertEqual(call_args[0][0], "WARNING")

    def test_alert_payload_construction_error_level(self):
        """Test that ERROR severity alert payload is constructed correctly."""
        with patch("common.alerting._log_alert") as mock_log:
            send_security_alert(
                event_type="Error Event",
                details="Error details",
                severity="ERROR",
            )
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            self.assertEqual(call_args[0][0], "ERROR")

    def test_alert_payload_construction_critical_level(self):
        """Test that CRITICAL severity alert payload is constructed correctly."""
        with patch("common.alerting._log_alert") as mock_log:
            send_security_alert(
                event_type="Critical Event",
                details="Critical details",
                severity="CRITICAL",
            )
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            self.assertEqual(call_args[0][0], "CRITICAL")

    def test_alert_payload_includes_metadata(self):
        """Test that alert payload includes metadata when provided."""
        metadata = {"ip": "192.168.1.1", "user_id": 123}
        with patch("common.alerting._log_alert") as mock_log:
            send_security_alert(
                event_type="Test Event",
                details="Test details",
                severity="INFO",
                metadata=metadata,
            )
            call_args = mock_log.call_args
            self.assertEqual(call_args[0][3], metadata)

    @patch("common.alerting.send_slack_alert")
    def test_slack_alert_delivery_triggered(self, mock_slack):
        """Test that Slack alert is triggered when webhook is configured."""
        with patch("common.alerting._log_alert"):
            with override_settings(SLACK_WEBHOOK_URL="https://hooks.slack.com/test"):
                send_security_alert(
                    event_type="Test Event",
                    details="Test details",
                    severity="WARNING",
                )
                mock_slack.assert_called_once()

    @patch("common.alerting.send_email_alert")
    def test_email_alert_delivery_for_error_severity(self, mock_email):
        """Test that email alert is triggered for ERROR severity."""
        with patch("common.alerting._log_alert"):
            with override_settings(SECURITY_TEAM_EMAILS=["security@example.com"]):
                send_security_alert(
                    event_type="Test Event",
                    details="Test details",
                    severity="ERROR",
                )
                mock_email.assert_called_once()

    @patch("common.alerting.send_email_alert")
    def test_email_alert_delivery_for_critical_severity(self, mock_email):
        """Test that email alert is triggered for CRITICAL severity."""
        with patch("common.alerting._log_alert"):
            with override_settings(SECURITY_TEAM_EMAILS=["security@example.com"]):
                send_security_alert(
                    event_type="Test Event",
                    details="Test details",
                    severity="CRITICAL",
                )
                mock_email.assert_called_once()

    @patch("common.alerting.send_email_alert")
    def test_email_alert_not_sent_for_warning_severity(self, mock_email):
        """Test that email alert is NOT sent for WARNING severity."""
        with patch("common.alerting._log_alert"):
            with override_settings(SECURITY_TEAM_EMAILS=["security@example.com"]):
                send_security_alert(
                    event_type="Test Event",
                    details="Test details",
                    severity="WARNING",
                )
                mock_email.assert_not_called()

    @patch("requests.post")
    def test_slack_payload_structure(self, mock_post):
        """Test that Slack payload has correct structure."""
        mock_post.return_value.raise_for_status = MagicMock()

        with override_settings(SLACK_WEBHOOK_URL="https://hooks.slack.com/test"):
            send_slack_alert("Test message", "WARNING")

        self.assertTrue(mock_post.called)
        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs["json"]

        # Verify payload structure
        self.assertIn("text", payload)
        self.assertIn("attachments", payload)
        self.assertTrue(len(payload["attachments"]) > 0)
        self.assertIn("color", payload["attachments"][0])
        self.assertIn("text", payload["attachments"][0])

    @patch("requests.post")
    def test_slack_color_mapping_by_severity(self, mock_post):
        """Test that Slack color is mapped correctly by severity."""
        mock_post.return_value.raise_for_status = MagicMock()

        color_map = {
            "INFO": "#36a64f",      # Green
            "WARNING": "#ff9900",   # Orange
            "ERROR": "#ff0000",     # Red
            "CRITICAL": "#8b0000",  # Dark red
        }

        with override_settings(SLACK_WEBHOOK_URL="https://hooks.slack.com/test"):
            for severity, expected_color in color_map.items():
                mock_post.reset_mock()
                send_slack_alert("Test message", severity)

                call_kwargs = mock_post.call_args[1]
                payload = call_kwargs["json"]
                actual_color = payload["attachments"][0]["color"]
                self.assertEqual(actual_color, expected_color)

    @patch("django.core.mail.send_mail")
    def test_email_alert_payload_structure(self, mock_send_mail):
        """Test that email alert has correct subject and message structure."""
        with override_settings(
            SECURITY_TEAM_EMAILS=["security@example.com"],
            DEFAULT_FROM_EMAIL="no-reply@example.com",
        ):
            send_email_alert("Test Subject", "Test message content", "ERROR")

        self.assertTrue(mock_send_mail.called)
        call_kwargs = mock_send_mail.call_args[1]

        # Verify email structure
        self.assertIn("ERROR", call_kwargs["subject"])
        self.assertIn("Test Subject", call_kwargs["subject"])
        self.assertIn("security@example.com", call_kwargs["recipient_list"])
        self.assertIn("no-reply@example.com", call_kwargs["from_email"])

    @patch("common.alerting.send_security_alert")
    def test_brute_force_alert_message(self, mock_alert):
        """Test that brute force alert includes required fields."""
        alert_brute_force_attack(
            ip_address="192.168.1.100",
            username="testuser",
            attempt_count=12,
        )

        mock_alert.assert_called_once()
        call_args = mock_alert.call_args
        self.assertEqual(call_args[1]["severity"], "CRITICAL")
        self.assertIn("Brute Force", call_args[1]["event_type"])

        # Verify metadata includes required fields
        metadata = call_args[1]["metadata"]
        self.assertEqual(metadata["ip"], "192.168.1.100")
        self.assertEqual(metadata["username"], "testuser")
        self.assertEqual(metadata["attempts"], 12)

    @patch("common.alerting.send_security_alert")
    def test_account_lockout_alert_message(self, mock_alert):
        """Test that account lockout alert includes required fields."""
        alert_account_lockout(
            username="testuser",
            ip_address="192.168.1.100",
            lockout_duration=30,
        )

        mock_alert.assert_called_once()
        call_args = mock_alert.call_args
        self.assertEqual(call_args[1]["severity"], "WARNING")
        self.assertIn("Account Lockout", call_args[1]["event_type"])

    @patch("common.alerting.send_security_alert")
    def test_suspicious_api_activity_alert_message(self, mock_alert):
        """Test that suspicious API activity alert includes required fields."""
        alert_suspicious_api_activity(
            path="/api/users/",
            error_rate=45.5,
            time_window=5,
        )

        mock_alert.assert_called_once()
        call_args = mock_alert.call_args
        self.assertEqual(call_args[1]["severity"], "WARNING")

    @patch("common.alerting.send_security_alert")
    def test_mass_data_export_alert_message(self, mock_alert):
        """Test that mass data export alert includes required fields."""
        alert_mass_data_export(
            user=self.test_user,
            export_type="CSV",
            record_count=10000,
        )

        mock_alert.assert_called_once()
        call_args = mock_alert.call_args
        self.assertEqual(call_args[1]["severity"], "WARNING")
        self.assertIn("Mass Data Export", call_args[1]["event_type"])

    @patch("common.alerting.send_security_alert")
    def test_unauthorized_access_alert_message(self, mock_alert):
        """Test that unauthorized access alert includes required fields."""
        alert_unauthorized_access(
            user=self.test_user,
            path="/admin/",
            permission_required="admin.add_user",
        )

        mock_alert.assert_called_once()
        call_args = mock_alert.call_args
        self.assertEqual(call_args[1]["severity"], "WARNING")
        self.assertIn("Unauthorized Access", call_args[1]["event_type"])

    @patch("common.alerting.send_security_alert")
    def test_admin_action_alert_message(self, mock_alert):
        """Test that admin action alert includes required fields."""
        alert_admin_action(
            admin_user=self.admin_user,
            action="DELETED_USER",
            target="user_id_123",
        )

        mock_alert.assert_called_once()
        call_args = mock_alert.call_args
        self.assertEqual(call_args[1]["severity"], "INFO")
        self.assertIn("Administrative Action", call_args[1]["event_type"])

    def test_alerting_configuration_check(self):
        """Test that alerting configuration status is correctly reported."""
        with override_settings(
            SLACK_WEBHOOK_URL="https://hooks.slack.com/test",
            SECURITY_TEAM_EMAILS=["security@example.com"],
        ):
            config = check_alerting_configuration()

            self.assertTrue(config["slack_configured"])
            self.assertTrue(config["email_configured"])
            self.assertTrue(config["logging_configured"])

    def test_alerting_configuration_check_missing_slack(self):
        """Test that missing Slack configuration is detected."""
        with override_settings(
            SLACK_WEBHOOK_URL=None,
            SECURITY_TEAM_EMAILS=["security@example.com"],
        ):
            config = check_alerting_configuration()

            self.assertFalse(config["slack_configured"])
            self.assertTrue(config["email_configured"])
            self.assertTrue(config["logging_configured"])

    def test_alerting_configuration_check_missing_email(self):
        """Test that missing email configuration is detected."""
        with override_settings(
            SLACK_WEBHOOK_URL="https://hooks.slack.com/test",
            SECURITY_TEAM_EMAILS=None,
        ):
            config = check_alerting_configuration()

            self.assertTrue(config["slack_configured"])
            self.assertFalse(config["email_configured"])
            self.assertTrue(config["logging_configured"])

    @patch("requests.post", side_effect=Exception("Connection timeout"))
    @patch("common.alerting._log_alert")
    def test_slack_delivery_failure_handling(self, mock_log, mock_post):
        """Test that Slack delivery failures are gracefully handled."""
        with override_settings(SLACK_WEBHOOK_URL="https://hooks.slack.com/test"):
            # Should not raise exception
            send_security_alert(
                event_type="Test Event",
                details="Test details",
                severity="WARNING",
            )
            # Logging should still happen
            mock_log.assert_called_once()

    @patch("django.core.mail.send_mail", side_effect=Exception("Email error"))
    @patch("common.alerting._log_alert")
    def test_email_delivery_failure_handling(self, mock_log, mock_send_mail):
        """Test that email delivery failures are gracefully handled."""
        with override_settings(SECURITY_TEAM_EMAILS=["security@example.com"]):
            # Should not raise exception
            send_security_alert(
                event_type="Test Event",
                details="Test details",
                severity="ERROR",
            )
            # Logging should still happen
            mock_log.assert_called_once()

    @patch("common.alerting._log_alert")
    def test_alert_includes_timestamp_in_metadata(self, mock_log):
        """Test that alert metadata includes timestamp."""
        send_security_alert(
            event_type="Test Event",
            details="Test details",
            severity="INFO",
            metadata={"key": "value"},
        )

        call_args = mock_log.call_args
        metadata = call_args[0][3]
        self.assertIn("timestamp", metadata)

    def test_multiple_severity_levels_in_batch(self):
        """Test handling multiple alert severity levels in sequence."""
        with patch("common.alerting._log_alert"):
            severities_to_test = ["INFO", "WARNING", "ERROR", "CRITICAL"]

            for severity in severities_to_test:
                send_security_alert(
                    event_type=f"Test {severity}",
                    details="Test details",
                    severity=severity,
                )

            # All should be logged without error
            self.assertTrue(True)
