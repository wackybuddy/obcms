"""Security middleware for production environments."""
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
import ipaddress
import logging


logger = logging.getLogger('rbac_security')


class ContentSecurityPolicyMiddleware(MiddlewareMixin):
    """
    Apply Content Security Policy headers to all responses.

    Mitigates:
    - Cross-Site Scripting (XSS) attacks
    - Clickjacking attacks
    - Code injection attacks

    Configuration:
        CONTENT_SECURITY_POLICY (str): CSP policy string from settings
        SECURE_REFERRER_POLICY (str): Referrer policy
        PERMISSIONS_POLICY (dict): Browser feature permissions
    """

    def process_response(self, request, response):
        """Add CSP header to response."""
        # Add Content Security Policy header
        if hasattr(settings, 'CONTENT_SECURITY_POLICY'):
            response['Content-Security-Policy'] = settings.CONTENT_SECURITY_POLICY

        # Add Referrer-Policy header
        if hasattr(settings, 'SECURE_REFERRER_POLICY'):
            response['Referrer-Policy'] = settings.SECURE_REFERRER_POLICY

        # Add Permissions-Policy header (formerly Feature-Policy)
        if hasattr(settings, 'PERMISSIONS_POLICY'):
            permissions = settings.PERMISSIONS_POLICY
            if isinstance(permissions, dict):
                policy_parts = []
                for feature, allowlist in permissions.items():
                    if allowlist:
                        policy_parts.append(f"{feature}=({' '.join(allowlist)})")
                    else:
                        policy_parts.append(f"{feature}=()")
                response['Permissions-Policy'] = ', '.join(policy_parts)

        return response


class AdminIPWhitelistMiddleware(MiddlewareMixin):
    """
    Restrict /admin/ access to whitelisted IP addresses.

    Mitigates:
    - Brute force attacks on admin panel
    - Unauthorized admin access attempts

    Configuration:
        ADMIN_IP_WHITELIST (list): List of allowed IPs/CIDR ranges
        Empty list = allow all (development mode)
    """

    def process_request(self, request):
        """Check IP address before allowing admin access."""
        if request.path.startswith('/admin/'):
            # Get client IP (handle proxy headers)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                # Get first IP in chain (client IP)
                client_ip = x_forwarded_for.split(',')[0].strip()
            else:
                client_ip = request.META.get('REMOTE_ADDR')

            # Get whitelist from settings
            whitelist = getattr(settings, 'ADMIN_IP_WHITELIST', [])

            # Empty whitelist = development mode (allow all)
            if not whitelist:
                return None

            # Check if IP is in whitelist (supports CIDR notation)
            try:
                client = ipaddress.ip_address(client_ip)
                for allowed in whitelist:
                    if '/' in allowed:  # CIDR notation
                        network = ipaddress.ip_network(allowed, strict=False)
                        if client in network:
                            return None
                    else:  # Single IP
                        if str(client) == allowed:
                            return None
            except (ValueError, AttributeError) as e:
                # Invalid IP address - log and deny
                logger.warning(
                    f"Invalid IP address in admin access attempt: {client_ip} - {e}"
                )
                raise PermissionDenied("Admin access restricted to whitelisted IP addresses")

            # IP not whitelisted - deny access
            logger.warning(
                f"Admin access denied for non-whitelisted IP: {client_ip} "
                f"accessing {request.path}"
            )
            raise PermissionDenied("Admin access restricted to whitelisted IP addresses")

        return None


class MetricsAuthenticationMiddleware(MiddlewareMixin):
    """
    Require authentication for Prometheus metrics endpoint.

    Mitigates:
    - Information disclosure via metrics
    - Reconnaissance attacks

    Configuration:
        METRICS_TOKEN (str): Bearer token for metrics access
    """

    def process_request(self, request):
        """Require token authentication for /metrics/ endpoint."""
        if request.path.startswith('/metrics/'):
            # Get authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')

            # Extract token
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove 'Bearer ' prefix
            else:
                token = ''

            # Get expected token from settings
            expected_token = getattr(settings, 'METRICS_TOKEN', '')

            # If no token configured, deny access (production safety)
            if not expected_token:
                logger.warning(
                    f"Metrics endpoint accessed but METRICS_TOKEN not configured "
                    f"(IP: {request.META.get('REMOTE_ADDR')})"
                )
                return HttpResponseForbidden(
                    "Metrics endpoint requires authentication. "
                    "Configure METRICS_TOKEN in settings."
                )

            # Validate token
            if token != expected_token:
                logger.warning(
                    f"Unauthorized metrics access attempt from IP: "
                    f"{request.META.get('REMOTE_ADDR')}"
                )
                return HttpResponseForbidden("Invalid metrics authentication token")

        return None
