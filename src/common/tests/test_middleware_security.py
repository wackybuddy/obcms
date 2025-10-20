"""Tests for security middleware."""
import pytest
from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from common.middleware.security import (
    ContentSecurityPolicyMiddleware,
    AdminIPWhitelistMiddleware,
    MetricsAuthenticationMiddleware,
)

User = get_user_model()


class ContentSecurityPolicyMiddlewareTest(TestCase):
    """Test CSP middleware."""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = ContentSecurityPolicyMiddleware(lambda r: HttpResponse())

    @override_settings(CONTENT_SECURITY_POLICY="default-src 'self'")
    def test_csp_header_added(self):
        """Test CSP header is added to responses."""
        request = self.factory.get('/')
        response = self.middleware(request)

        self.assertIn('Content-Security-Policy', response)
        self.assertEqual(response['Content-Security-Policy'], "default-src 'self'")

    def test_no_csp_header_when_not_configured(self):
        """Test no CSP header when CONTENT_SECURITY_POLICY not set."""
        request = self.factory.get('/')
        response = self.middleware(request)

        # Should not have CSP header if not configured
        self.assertNotIn('Content-Security-Policy', response)

    @override_settings(
        SECURE_REFERRER_POLICY="strict-origin-when-cross-origin",
    )
    def test_referrer_policy_header(self):
        """Test referrer policy header is added."""
        request = self.factory.get('/')
        response = self.middleware(request)

        self.assertIn('Referrer-Policy', response)
        self.assertEqual(
            response['Referrer-Policy'],
            "strict-origin-when-cross-origin"
        )

    @override_settings(
        PERMISSIONS_POLICY={"camera": [], "microphone": [], "geolocation": ["self"]}
    )
    def test_permissions_policy_header(self):
        """Test permissions policy header is added."""
        request = self.factory.get('/')
        response = self.middleware(request)

        self.assertIn('Permissions-Policy', response)
        policy = response['Permissions-Policy']

        # Check that all features are present
        self.assertIn('camera=()', policy)
        self.assertIn('microphone=()', policy)
        self.assertIn('geolocation=(self)', policy)

    @override_settings(
        CONTENT_SECURITY_POLICY="default-src 'self'",
        SECURE_REFERRER_POLICY="strict-origin-when-cross-origin",
        PERMISSIONS_POLICY={"camera": [], "microphone": []}
    )
    def test_all_headers_added_together(self):
        """Test all security headers can be added together."""
        request = self.factory.get('/')
        response = self.middleware(request)

        self.assertIn('Content-Security-Policy', response)
        self.assertIn('Referrer-Policy', response)
        self.assertIn('Permissions-Policy', response)


class AdminIPWhitelistMiddlewareTest(TestCase):
    """Test admin IP whitelist middleware."""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = AdminIPWhitelistMiddleware(lambda r: HttpResponse())

    @override_settings(ADMIN_IP_WHITELIST=[])
    def test_empty_whitelist_allows_all(self):
        """Test empty whitelist allows all IPs (development mode)."""
        request = self.factory.get('/admin/')
        request.META['REMOTE_ADDR'] = '1.2.3.4'

        response = self.middleware(request)
        self.assertIsNone(response)  # None = allowed to proceed

    @override_settings(ADMIN_IP_WHITELIST=['192.168.1.100'])
    def test_whitelisted_ip_allowed(self):
        """Test whitelisted IP is allowed."""
        request = self.factory.get('/admin/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'

        response = self.middleware(request)
        self.assertIsNone(response)

    @override_settings(ADMIN_IP_WHITELIST=['192.168.1.100'])
    def test_non_whitelisted_ip_denied(self):
        """Test non-whitelisted IP is denied."""
        request = self.factory.get('/admin/')
        request.META['REMOTE_ADDR'] = '1.2.3.4'

        with self.assertRaises(PermissionDenied):
            self.middleware(request)

    @override_settings(ADMIN_IP_WHITELIST=['10.0.0.0/24'])
    def test_cidr_range_allowed(self):
        """Test CIDR range matching works."""
        request = self.factory.get('/admin/')
        request.META['REMOTE_ADDR'] = '10.0.0.50'

        response = self.middleware(request)
        self.assertIsNone(response)

    @override_settings(ADMIN_IP_WHITELIST=['10.0.0.0/24'])
    def test_cidr_range_denied(self):
        """Test IP outside CIDR range is denied."""
        request = self.factory.get('/admin/')
        request.META['REMOTE_ADDR'] = '10.0.1.50'

        with self.assertRaises(PermissionDenied):
            self.middleware(request)

    @override_settings(ADMIN_IP_WHITELIST=['192.168.1.100'])
    def test_x_forwarded_for_header(self):
        """Test X-Forwarded-For header is respected (proxy support)."""
        request = self.factory.get('/admin/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.100, 10.0.0.1'
        request.META['REMOTE_ADDR'] = '10.0.0.1'  # Proxy IP

        # Should use first IP in X-Forwarded-For chain
        response = self.middleware(request)
        self.assertIsNone(response)

    @override_settings(ADMIN_IP_WHITELIST=['192.168.1.100'])
    def test_non_admin_path_not_checked(self):
        """Test non-admin paths are not checked."""
        request = self.factory.get('/api/users/')
        request.META['REMOTE_ADDR'] = '1.2.3.4'

        response = self.middleware(request)
        self.assertIsNone(response)  # Should pass through

    @override_settings(ADMIN_IP_WHITELIST=['192.168.1.100', '10.0.0.0/16'])
    def test_multiple_whitelist_entries(self):
        """Test multiple whitelist entries work correctly."""
        # Test first IP
        request1 = self.factory.get('/admin/')
        request1.META['REMOTE_ADDR'] = '192.168.1.100'
        self.assertIsNone(self.middleware(request1))

        # Test CIDR range
        request2 = self.factory.get('/admin/')
        request2.META['REMOTE_ADDR'] = '10.0.5.50'
        self.assertIsNone(self.middleware(request2))

        # Test non-whitelisted
        request3 = self.factory.get('/admin/')
        request3.META['REMOTE_ADDR'] = '1.2.3.4'
        with self.assertRaises(PermissionDenied):
            self.middleware(request3)


class MetricsAuthenticationMiddlewareTest(TestCase):
    """Test metrics authentication middleware."""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = MetricsAuthenticationMiddleware(lambda r: HttpResponse())

    @override_settings(METRICS_TOKEN='test-token-12345')
    def test_valid_token_allowed(self):
        """Test valid token allows access."""
        request = self.factory.get('/metrics/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer test-token-12345'

        response = self.middleware(request)
        self.assertIsNone(response)

    @override_settings(METRICS_TOKEN='test-token-12345')
    def test_invalid_token_denied(self):
        """Test invalid token denies access."""
        request = self.factory.get('/metrics/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer wrong-token'

        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Invalid metrics authentication token', response.content)

    @override_settings(METRICS_TOKEN='test-token-12345')
    def test_missing_token_denied(self):
        """Test missing token denies access."""
        request = self.factory.get('/metrics/')

        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)

    @override_settings(METRICS_TOKEN='')
    def test_no_token_configured_denies_access(self):
        """Test no token configured denies all access."""
        request = self.factory.get('/metrics/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer any-token'

        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'METRICS_TOKEN', response.content)

    @override_settings(METRICS_TOKEN='test-token-12345')
    def test_malformed_authorization_header(self):
        """Test malformed authorization header denies access."""
        request = self.factory.get('/metrics/')
        request.META['HTTP_AUTHORIZATION'] = 'test-token-12345'  # Missing 'Bearer '

        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)

    @override_settings(METRICS_TOKEN='test-token-12345')
    def test_non_metrics_path_not_checked(self):
        """Test non-metrics paths are not checked."""
        request = self.factory.get('/api/users/')

        response = self.middleware(request)
        self.assertIsNone(response)  # Should pass through

    @override_settings(METRICS_TOKEN='test-token-12345')
    def test_metrics_subpath_protected(self):
        """Test metrics subpaths are also protected."""
        request = self.factory.get('/metrics/prometheus')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer test-token-12345'

        response = self.middleware(request)
        self.assertIsNone(response)

    @override_settings(METRICS_TOKEN='test-token-12345')
    def test_case_sensitive_token(self):
        """Test token matching is case-sensitive."""
        request = self.factory.get('/metrics/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer TEST-TOKEN-12345'

        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)


class SecurityMiddlewareIntegrationTest(TestCase):
    """Integration tests for security middleware working together."""

    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(
        CONTENT_SECURITY_POLICY="default-src 'self'",
        ADMIN_IP_WHITELIST=['192.168.1.100'],
        METRICS_TOKEN='test-token'
    )
    def test_all_middleware_can_coexist(self):
        """Test all security middleware can work together."""
        # Create middleware chain
        def final_handler(request):
            return HttpResponse('OK')

        metrics_middleware = MetricsAuthenticationMiddleware(final_handler)
        admin_middleware = AdminIPWhitelistMiddleware(metrics_middleware)
        csp_middleware = ContentSecurityPolicyMiddleware(admin_middleware)

        # Test regular request gets CSP headers
        request = self.factory.get('/')
        response = csp_middleware(request)
        self.assertIn('Content-Security-Policy', response)

        # Test admin request is IP-checked
        admin_request = self.factory.get('/admin/')
        admin_request.META['REMOTE_ADDR'] = '1.2.3.4'
        with self.assertRaises(PermissionDenied):
            csp_middleware(admin_request)

        # Test metrics request requires token
        metrics_request = self.factory.get('/metrics/')
        response = csp_middleware(metrics_request)
        self.assertEqual(response.status_code, 403)
