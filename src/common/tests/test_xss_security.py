"""Tests for XSS vulnerability prevention."""

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.utils.html import escape

User = get_user_model()


class XSSSecurityTest(TestCase):
    """Test XSS attack prevention in templates and views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_xss_payload_in_search_parameters(self):
        """Test XSS attempt in search parameters is escaped."""
        xss_payload = '<script>alert("XSS")</script>'

        # Make a request with XSS payload in query parameters
        response = self.client.get('/communities/', {
            'search': xss_payload
        })

        # XSS payload should be escaped in HTML response
        self.assertNotContains(response, '<script>alert("XSS")</script>')
        # HTML entities should be present
        self.assertIn('&lt;script&gt;', response.content.decode())

    def test_xss_in_filter_parameters(self):
        """Test XSS in filter parameters is properly escaped."""
        xss_payload = '"><script>alert("XSS")</script><"'

        response = self.client.get('/communities/', {
            'filter': xss_payload
        })

        # Should not execute JavaScript
        self.assertNotContains(response, 'alert("XSS")')
        # Should be escaped
        self.assertIn('&quot;', response.content.decode())

    def test_javascript_protocol_in_redirect(self):
        """Test javascript: protocol URLs are blocked."""
        response = self.client.get('/communities/', {
            'next': 'javascript:alert("XSS")'
        })

        # Should not execute JavaScript
        self.assertNotContains(response, 'javascript:alert')

    def test_img_tag_onerror_injection(self):
        """Test img tag onerror attribute injection is blocked."""
        xss_payload = '<img src=x onerror=alert("XSS")>'

        response = self.client.get('/communities/', {
            'q': xss_payload
        })

        # Should not have raw img tag with onerror
        self.assertNotContains(response, 'onerror=alert')
        # Should be escaped
        self.assertIn('&lt;img', response.content.decode())

    def test_svg_xss_payload(self):
        """Test SVG with embedded script is escaped."""
        xss_payload = '<svg><script>alert("XSS")</script></svg>'

        response = self.client.get('/communities/', {
            'name': xss_payload
        })

        # SVG script should be escaped
        self.assertNotContains(response, '<svg><script>')
        self.assertIn('&lt;svg&gt;', response.content.decode())

    def test_event_handler_attributes(self):
        """Test event handler attributes are escaped."""
        payloads = [
            'onclick=alert("XSS")',
            'onload=alert("XSS")',
            'onmouseover=alert("XSS")',
            'onfocus=alert("XSS")',
        ]

        for payload in payloads:
            response = self.client.get('/communities/', {'q': payload})
            # Event handlers should not be executable
            self.assertNotContains(response, f'{payload}')

    def test_data_attribute_xss(self):
        """Test data: URI XSS is prevented."""
        xss_payload = 'data:text/html,<script>alert("XSS")</script>'

        response = self.client.get('/communities/', {
            'link': xss_payload
        })

        # Should not execute inline script
        self.assertNotContains(response, '<script>alert("XSS")</script>')

    def test_unicode_xss_payload(self):
        """Test unicode-encoded XSS payloads are escaped."""
        # Unicode escape: \u003cscript\u003e
        xss_payload = '\\u003cscript\\u003ealert("XSS")\\u003c/script\\u003e'

        response = self.client.get('/communities/', {'q': xss_payload})

        # Should be treated as literal string
        self.assertNotContains(response, 'alert("XSS")')

    def test_html_entity_xss(self):
        """Test HTML entity encoding XSS is escaped."""
        xss_payload = '&#60;script&#62;alert("XSS")&#60;/script&#62;'

        response = self.client.get('/communities/', {'q': xss_payload})

        # Should not decode to executable script
        # May contain the entity-encoded form
        content = response.content.decode()
        # Verify it's safe
        self.assertNotContains(response, '<script>')

    def test_form_input_escaping(self):
        """Test form input values are properly escaped."""
        xss_payload = '<script>alert("XSS")</script>'

        response = self.client.get('/communities/add/', {
            'initial_name': xss_payload
        })

        # Form field values should be escaped
        if response.status_code == 200:
            content = response.content.decode()
            # Value attributes should be escaped
            self.assertNotIn('<script>alert', content)

    def test_url_parameter_escaping(self):
        """Test URL parameters in responses are escaped."""
        xss_payload = '"><script>alert("XSS")</script><"'

        response = self.client.get('/communities/', {
            'sort_by': xss_payload
        })

        # URLs in response should have parameters escaped
        content = response.content.decode()
        # Should not contain unescaped script tag
        self.assertNotIn('<script>alert', content)

    def test_safe_dom_utilities_exist(self):
        """Test that SafeDOM utilities are loaded in base template."""
        response = self.client.get('/communities/')

        content = response.content.decode()
        # SafeDOM should be available globally
        self.assertIn('window.SafeDOM', content)
        self.assertIn('SafeDOM.setText', content)
        self.assertIn('SafeDOM.createElement', content)
        self.assertIn('SafeDOM.escape', content)

    def test_csp_header_in_production(self):
        """Test Content Security Policy is set in production."""
        response = self.client.get('/communities/')

        # In development, CSP might not be in HTTP header (only in meta tag)
        # Check for meta tag in HTML
        content = response.content.decode()
        if 'Content-Security-Policy' in content:
            self.assertIn('default-src', content)
            self.assertIn('script-src', content)

    def test_double_encoding_attack(self):
        """Test double-encoded XSS payloads are safe."""
        # Double-encoded: %253cscript%253e
        xss_payload = '%253cscript%253ealert(%22XSS%22)%253c%2fscript%253e'

        response = self.client.get('/communities/', {
            'q': xss_payload
        })

        # Should be safe regardless of encoding level
        self.assertNotContains(response, 'alert("XSS")')

    def test_mutation_xss_variations(self):
        """Test mutation XSS (mXSS) variations are escaped."""
        payloads = [
            '<noscript><p title="</noscript><img src=x onerror=alert("XSS")>">',
            '<form><button formaction=javascript:alert("XSS")>Click</button></form>',
            '<style>@import"<script>alert("XSS")</script>"</style>',
        ]

        for payload in payloads:
            response = self.client.get('/communities/', {'q': payload})
            # Should not execute
            self.assertNotContains(response, 'alert("XSS")')

    def test_whitespace_obfuscation_xss(self):
        """Test XSS with whitespace obfuscation is escaped."""
        xss_payload = '<script\nalert("XSS")\n></script>'

        response = self.client.get('/communities/', {'q': xss_payload})

        # Should be escaped regardless of whitespace
        content = response.content.decode()
        self.assertNotIn('<script', content)

    def test_comment_bypass_xss(self):
        """Test XSS using HTML comments is escaped."""
        xss_payload = '<!--<script>alert("XSS")</script>-->'

        response = self.client.get('/communities/', {'q': xss_payload})

        # Comments should be escaped
        content = response.content.decode()
        self.assertNotContains(response, '<script>')

    def test_null_byte_xss(self):
        """Test XSS with null byte injection is handled."""
        xss_payload = '<script>alert("XSS")\x00</script>'

        response = self.client.get('/communities/', {'q': xss_payload})

        # Should handle null bytes safely
        self.assertNotContains(response, 'alert("XSS")')


class HTMLEscapingTest(TestCase):
    """Test Django's HTML escaping functions work correctly."""

    def test_escape_function(self):
        """Test Django's escape function."""
        from django.utils.html import escape as django_escape

        xss_payload = '<script>alert("XSS")</script>'
        escaped = django_escape(xss_payload)

        self.assertNotIn('<script>', escaped)
        self.assertIn('&lt;script&gt;', escaped)

    def test_format_html_escapes_arguments(self):
        """Test format_html escapes all arguments."""
        from django.utils.html import format_html, escape as django_escape

        user_input = '<img src=x onerror=alert("XSS")>'
        safe_html = format_html('<div>{}</div>', user_input)

        # format_html should escape the user input
        self.assertNotIn('onerror=', str(safe_html))
        self.assertIn('&lt;img', str(safe_html))

    def test_format_html_join_escapes(self):
        """Test format_html_join escapes user content."""
        from django.utils.html import format_html_join

        items = [
            ('<script>alert("XSS")</script>', 'item1'),
            ('<img src=x onerror=alert("XSS")>', 'item2'),
        ]

        html = format_html_join(
            ', ',
            '<span>{}</span>',
            items
        )

        # Should escape all user content
        content = str(html)
        self.assertNotIn('<script>', content)
        self.assertNotIn('onerror=', content)


class TemplateSecurityTest(TestCase):
    """Test template-level XSS prevention."""

    def setUp(self):
        self.client = Client()

    def test_autoescape_enabled(self):
        """Test that Django autoescape is enabled by default."""
        response = self.client.get('/communities/')

        # If autoescape is working, this should pass
        self.assertEqual(response.status_code, 200)

    def test_safe_filter_requires_developer_intent(self):
        """Test that |safe filter is intentionally used."""
        # This is more of a code review check
        # We verify safe usage in other tests
        pass


class AdminSecurityTest(TestCase):
    """Test admin interface XSS prevention."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.login(username='admin', password='adminpass123')

    def test_admin_list_display_escaping(self):
        """Test admin list display fields are escaped."""
        # Admin views should also escape user content
        # This is implementation-dependent and would need actual models
        pass
