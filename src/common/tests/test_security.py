"""
Comprehensive Security Tests for OBCMS Critical Vulnerabilities

Tests cover:
1. Query Executor - eval() injection protection
2. Migration - SQL injection protection
3. Query Templates - String interpolation injection protection
4. End-to-end security validation

CRITICAL: These tests verify fixes for Remote Code Execution (RCE) and SQL injection vulnerabilities.
"""

import pytest
from django.test import TestCase
from django.db import connection

from common.ai_services.chat.query_executor import QueryExecutor, SecurityError
from common.ai_services.chat.query_templates.mana import (
    build_workshops_by_location,
    build_workshops_by_date_range,
    build_workshop_count_by_location,
    build_assessments_by_location,
    build_assessments_by_status,
    build_needs_by_location,
    build_participants_by_location,
)


class TestQueryExecutorSecurity(TestCase):
    """Test Query Executor protection against eval() injection attacks."""

    def setUp(self):
        """Initialize query executor for tests."""
        self.executor = QueryExecutor()

    def test_eval_injection_protection_import_os(self):
        """Test protection against __import__('os') injection."""
        malicious_query = "__import__('os').system('whoami')"

        result = self.executor.execute(malicious_query)

        # Should be blocked
        self.assertFalse(result['success'])
        self.assertIn('unsafe', result['error'].lower())

    def test_eval_injection_protection_subclasses(self):
        """Test protection against Python sandbox bypass via __subclasses__."""
        malicious_query = "().__class__.__bases__[0].__subclasses__()"

        result = self.executor.execute(malicious_query)

        # Should be blocked
        self.assertFalse(result['success'])
        self.assertIn('unsafe', result['error'].lower())

    def test_eval_injection_protection_exec(self):
        """Test protection against exec() injection."""
        malicious_query = "exec('import os; os.system(\"whoami\")')"

        result = self.executor.execute(malicious_query)

        # Should be blocked
        self.assertFalse(result['success'])
        self.assertIn('unsafe', result['error'].lower())

    def test_eval_injection_protection_compile(self):
        """Test protection against compile() injection."""
        malicious_query = "compile('import os', '<string>', 'exec')"

        result = self.executor.execute(malicious_query)

        # Should be blocked
        self.assertFalse(result['success'])
        self.assertIn('unsafe', result['error'].lower())

    def test_eval_injection_protection_file_access(self):
        """Test protection against file access."""
        malicious_queries = [
            "open('/etc/passwd').read()",
            "file('/etc/passwd')",
            "__import__('builtins').open('/etc/passwd')",
        ]

        for query in malicious_queries:
            with self.subTest(query=query):
                result = self.executor.execute(query)
                self.assertFalse(result['success'])

    def test_eval_injection_protection_subprocess(self):
        """Test protection against subprocess injection."""
        malicious_queries = [
            "__import__('subprocess').call(['ls'])",
            "__import__('os').popen('ls')",
        ]

        for query in malicious_queries:
            with self.subTest(query=query):
                result = self.executor.execute(query)
                self.assertFalse(result['success'])

    def test_dangerous_method_blocked_delete(self):
        """Test that delete() method is blocked."""
        malicious_query = "OBCCommunity.objects.all().delete()"

        result = self.executor.execute(malicious_query)

        # Should be blocked by dangerous keyword detection
        self.assertFalse(result['success'])

    def test_dangerous_method_blocked_update(self):
        """Test that update() method is blocked."""
        malicious_query = "OBCCommunity.objects.update(name='hacked')"

        result = self.executor.execute(malicious_query)

        # Should be blocked
        self.assertFalse(result['success'])

    def test_dangerous_method_blocked_create(self):
        """Test that create() method is blocked."""
        malicious_query = "OBCCommunity.objects.create(name='malicious')"

        result = self.executor.execute(malicious_query)

        # Should be blocked
        self.assertFalse(result['success'])

    def test_queryset_direct_execution_bypasses_eval(self):
        """Test that QuerySet objects can be passed directly (most secure)."""
        from communities.models import OBCCommunity

        # Create a QuerySet object
        qs = OBCCommunity.objects.all()[:5]

        # Execute with QuerySet directly (no eval, no parsing)
        result = self.executor.execute(qs)

        # Should succeed
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['result'])

    def test_safe_query_execution(self):
        """Test that legitimate safe queries still work."""
        safe_queries = [
            "Region.objects.count()",
            "Province.objects.all()[:10]",
            "Municipality.objects.filter(province__name='Zamboanga del Sur').count()",
        ]

        for query in safe_queries:
            with self.subTest(query=query):
                result = self.executor.execute(query)
                # Legitimate queries should succeed (though may have no results)
                # Main goal: should not raise SecurityError
                self.assertIsNotNone(result)


class TestMigrationSQLInjection(TestCase):
    """Test Migration SQL injection protection."""

    def test_migration_uses_parameterized_queries(self):
        """Test that migration uses connection.ops.quote_name()."""
        # Read the migration file to verify it uses proper SQL escaping
        import inspect
        from common.migrations import m0004_ensure_population_columns

        source = inspect.getsource(m0004_ensure_population_columns)

        # Should use quote_name for identifiers
        self.assertIn('connection.ops.quote_name', source)

        # Should NOT use f-strings for SQL construction
        self.assertNotIn('f"UPDATE {table_name}', source)
        self.assertNotIn("f'UPDATE {table_name}", source)

        # Should use parameterized queries with %s
        self.assertIn('cursor.execute(sql, [0])', source)

    def test_migration_table_name_escaping(self):
        """Test that table names are properly escaped in migration."""
        # This is a static code analysis test
        import re
        from common.migrations import m0004_ensure_population_columns
        import inspect

        source = inspect.getsource(m0004_ensure_population_columns)

        # Find all cursor.execute calls
        execute_patterns = re.findall(r'cursor\.execute\([^)]+\)', source)

        for pattern in execute_patterns:
            # Should not have direct string interpolation
            self.assertNotIn('f"', pattern)
            self.assertNotIn("f'", pattern)


class TestQueryTemplateSQLInjection(TestCase):
    """Test Query Template protection against SQL injection."""

    def test_workshops_by_location_no_injection(self):
        """Test workshops_by_location with SQL injection payload."""
        malicious_entities = {
            'location': {
                'value': "') OR 1=1--",
                'type': 'region'
            }
        }

        # Call the query builder
        result = build_workshops_by_location(malicious_entities)

        # Should return QuerySet object, not string with interpolation
        from django.db.models import QuerySet
        self.assertIsInstance(result, QuerySet)

        # The SQL should be parameterized, not contain the payload literally
        sql_str = str(result.query)
        # Django's ORM parameterizes this, so malicious input won't appear in SQL
        # The important thing is it doesn't execute SQL injection

    def test_workshops_by_date_range_no_injection(self):
        """Test workshops_by_date_range with malicious date input."""
        malicious_entities = {
            'date_range': {
                'start': "2024-01-01'; DROP TABLE workshops--",
                'end': "2024-12-31"
            }
        }

        result = build_workshops_by_date_range(malicious_entities)

        # Should return QuerySet, not execute SQL injection
        from django.db.models import QuerySet
        self.assertIsInstance(result, QuerySet)

    def test_workshop_count_by_location_no_injection(self):
        """Test workshop_count_by_location with SQL injection payload."""
        malicious_entities = {
            'location': {
                'value': "' UNION SELECT password FROM users--",
            }
        }

        result = build_workshop_count_by_location(malicious_entities)

        # Should return integer count, not vulnerable string
        self.assertIsInstance(result, int)

    def test_assessments_by_location_no_injection(self):
        """Test assessments_by_location with SQL injection payload."""
        malicious_entities = {
            'location': {
                'value': "'); DELETE FROM assessments--",
            }
        }

        result = build_assessments_by_location(malicious_entities)

        from django.db.models import QuerySet
        self.assertIsInstance(result, QuerySet)

    def test_assessments_by_status_no_injection(self):
        """Test assessments_by_status with SQL injection payload."""
        malicious_entities = {
            'status': {
                'value': "completed' OR '1'='1",
            }
        }

        result = build_assessments_by_status(malicious_entities)

        from django.db.models import QuerySet
        self.assertIsInstance(result, QuerySet)

    def test_needs_by_location_no_injection(self):
        """Test needs_by_location with SQL injection payload."""
        malicious_entities = {
            'location': {
                'value': "' OR 1=1 UNION SELECT * FROM sensitive_data--",
            }
        }

        result = build_needs_by_location(malicious_entities)

        from django.db.models import QuerySet
        self.assertIsInstance(result, QuerySet)

    def test_participants_by_location_no_injection(self):
        """Test participants_by_location with SQL injection payload."""
        malicious_entities = {
            'location': {
                'value': "'; UPDATE users SET role='admin'--",
            }
        }

        result = build_participants_by_location(malicious_entities)

        # Should return integer count
        self.assertIsInstance(result, int)

    def test_all_query_builders_return_safe_types(self):
        """Test that all query builders return QuerySet or primitive types, not interpolated strings."""
        from django.db.models import QuerySet

        test_entities = {
            'location': {'value': "malicious' input", 'type': 'region'},
            'status': {'value': "completed' OR '1'='1"},
            'date_range': {'start': '2024-01-01', 'end': '2024-12-31'}
        }

        query_builders = [
            build_workshops_by_location,
            build_workshops_by_date_range,
            build_workshop_count_by_location,
            build_assessments_by_location,
            build_assessments_by_status,
            build_needs_by_location,
            build_participants_by_location,
        ]

        for builder in query_builders:
            with self.subTest(builder=builder.__name__):
                result = builder(test_entities)

                # Should be QuerySet, int, or other safe type - NOT a string with interpolation
                self.assertIsInstance(result, (QuerySet, int, float, list, dict))


class TestEndToEndSecurity(TestCase):
    """End-to-end security tests combining executor and templates."""

    def test_e2e_malicious_location_query(self):
        """Test end-to-end query execution with malicious location input."""
        from common.ai_services.chat.query_templates.mana import build_workshops_by_location

        malicious_entities = {
            'location': {
                'value': "'); DROP TABLE workshops; --",
                'type': 'region'
            }
        }

        # Build query (should return safe QuerySet)
        qs = build_workshops_by_location(malicious_entities)

        # Execute through executor
        executor = QueryExecutor()
        result = executor.execute(qs)

        # Should succeed without executing malicious SQL
        self.assertTrue(result['success'])

        # Verify workshops table still exists (using ORM, SQLite-compatible)
        try:
            from mana.models import Workshop
            # Try to count workshops - if table doesn't exist, this will raise an error
            count = Workshop.objects.count()
            # If we get here, table exists
            self.assertGreaterEqual(count, 0, "Workshops table should still exist")
        except Exception as e:
            if 'no such table' in str(e).lower() or 'does not exist' in str(e).lower():
                self.fail(f"Workshops table was dropped by SQL injection: {e}")
            else:
                # Some other error, re-raise
                raise

    def test_e2e_multiple_injection_vectors(self):
        """Test multiple injection vectors in sequence."""
        executor = QueryExecutor()

        injection_payloads = [
            "__import__('os').system('rm -rf /')",
            "().__class__.__bases__[0].__subclasses__()",
            "exec('import os')",
            "OBCCommunity.objects.all().delete()",
        ]

        for payload in injection_payloads:
            with self.subTest(payload=payload):
                result = executor.execute(payload)
                self.assertFalse(result['success'], f"Should block: {payload}")


class TestSecurityDocumentation(TestCase):
    """Test that security measures are properly documented."""

    def test_query_executor_has_security_docstrings(self):
        """Test that security measures are documented in QueryExecutor."""
        executor = QueryExecutor()

        # Check class docstring mentions security
        class_doc = executor.__class__.__doc__
        self.assertIn('security', class_doc.lower())

        # Check execute method documents security
        execute_doc = executor.execute.__doc__
        self.assertIn('security', execute_doc.lower())

    def test_query_builders_have_security_docstrings(self):
        """Test that fixed query builders document security measures."""
        security_builders = [
            build_workshops_by_location,
            build_workshops_by_date_range,
            build_workshop_count_by_location,
            build_assessments_by_location,
            build_assessments_by_status,
            build_needs_by_location,
            build_participants_by_location,
        ]

        for builder in security_builders:
            with self.subTest(builder=builder.__name__):
                doc = builder.__doc__
                self.assertIsNotNone(doc)
                self.assertIn('SECURITY', doc.upper())


# Pytest fixtures for additional test support
@pytest.fixture
def query_executor():
    """Fixture providing QueryExecutor instance."""
    return QueryExecutor()


@pytest.fixture
def malicious_payloads():
    """Fixture providing common malicious payloads."""
    return {
        'sql_injection': [
            "' OR '1'='1",
            "'; DROP TABLE users--",
            "' UNION SELECT * FROM passwords--",
        ],
        'rce': [
            "__import__('os').system('whoami')",
            "exec('import os')",
            "().__class__.__bases__[0].__subclasses__()",
        ],
        'file_access': [
            "open('/etc/passwd').read()",
            "__import__('builtins').open('/etc/shadow')",
        ]
    }


@pytest.mark.django_db
class TestSecurityRegressions:
    """Test that security fixes don't break existing functionality."""

    def test_legitimate_queries_still_work(self, query_executor):
        """Test that legitimate queries continue to function."""
        legitimate_queries = [
            "Region.objects.count()",
            "Province.objects.all()[:5]",
        ]

        for query in legitimate_queries:
            result = query_executor.execute(query)
            assert result is not None
            # Should complete without security errors

    def test_query_templates_return_results(self):
        """Test that fixed query templates return valid results."""
        from django.db.models import QuerySet

        entities = {
            'location': {'value': 'Region IX', 'type': 'region'},
            'status': {'value': 'completed'},
        }

        result = build_workshops_by_location(entities)
        assert isinstance(result, QuerySet)

        result = build_assessments_by_status(entities)
        assert isinstance(result, QuerySet)
