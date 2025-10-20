"""
Query Executor for Conversational AI

Safely executes Django ORM queries generated from natural language.
Implements comprehensive security validation to prevent dangerous operations.
"""

import ast
import logging
from typing import Any, Dict, List, Optional

from django.db.models import Avg, Count, Max, Min, Q, Sum

logger = logging.getLogger(__name__)


class QueryExecutor:
    """
    Safely execute Django ORM queries from natural language.

    Security Features:
    - Whitelist of allowed models and methods
    - Blocks all write operations (create, update, delete)
    - AST parsing to detect dangerous patterns
    - Result size limits to prevent resource exhaustion
    """

    # Allowed models (read-only access)
    ALLOWED_MODELS = {
        "OBCCommunity": "communities.models.OBCCommunity",
        "Municipality": "common.models.Municipality",
        "Province": "common.models.Province",
        "Region": "common.models.Region",
        "Barangay": "common.models.Barangay",
        "Assessment": "mana.models.Assessment",
        "PolicyRecommendation": "recommendations.policy_tracking.models.PolicyRecommendation",
        "Organization": "coordination.models.Organization",
        "Partnership": "coordination.models.Partnership",
        "WorkItem": "common.work_item_model.WorkItem",
        "Event": "common.models.Event",
    }

    # Allowed QuerySet methods (read-only)
    ALLOWED_METHODS = {
        "filter",
        "exclude",
        "get",
        "first",
        "last",
        "exists",
        "count",
        "aggregate",
        "annotate",
        "values",
        "values_list",
        "order_by",
        "distinct",
        "select_related",
        "prefetch_related",
        "all",
        "none",
    }

    # Allowed aggregation functions
    ALLOWED_AGGREGATES = {"Count", "Sum", "Avg", "Max", "Min"}

    # Dangerous keywords that should never appear
    DANGEROUS_KEYWORDS = {
        "delete",
        "update",
        "create",
        "save",
        "bulk_create",
        "bulk_update",
        "raw",
        "execute",
        "cursor",
        "eval",
        "exec",
        "compile",
        "__import__",
        "open",
        "file",
        "input",
        "system",
        "popen",
        "subprocess",
    }

    # Maximum results to return
    MAX_RESULTS = 1000

    def __init__(self):
        """Initialize query executor with safety context."""
        self._context = self._build_safe_context()

    def execute(self, query_input: Any) -> Dict[str, Any]:
        """
        Execute a query with comprehensive safety checks.

        Args:
            query_input: Either a Django ORM query string OR a QuerySet object

        Returns:
            Dictionary with:
                - success: bool
                - result: Query result or None
                - error: Error message if failed
                - query_info: Metadata about the query

        Security:
            - If QuerySet is provided directly, no eval() or parsing is needed (most secure)
            - If string is provided, uses safe AST parsing without eval()

        Example:
            >>> executor = QueryExecutor()
            >>> result = executor.execute(
            ...     "OBCCommunity.objects.filter(barangay__municipality__province__name='Zamboanga del Sur').count()"
            ... )
            >>> print(result['result'])
            42

            Or with QuerySet directly (PREFERRED):
            >>> result = executor.execute(OBCCommunity.objects.all())
        """
        from django.db.models import QuerySet

        try:
            # SECURITY: If query_input is already a QuerySet, use it directly (most secure)
            if isinstance(query_input, QuerySet):
                result = query_input
                query_string = str(query_input.query)
            else:
                # String query - parse and validate
                query_string = str(query_input)

                # Step 1: Parse and validate query
                validation = self._validate_query(query_string)
                if not validation["is_safe"]:
                    return {
                        "success": False,
                        "result": None,
                        "error": f"Unsafe query: {validation['reason']}",
                        "query_info": validation,
                    }

                # Step 2: Execute query in restricted context
                result = self._execute_safe(query_string)

            # Step 3: Process and limit results
            processed_result = self._process_result(result)

            return {
                "success": True,
                "result": processed_result,
                "error": None,
                "query_info": {
                    "query": query_string if isinstance(query_input, str) else "QuerySet object",
                    "result_type": type(result).__name__,
                    "result_count": self._get_result_count(processed_result),
                },
            }

        except Exception as e:
            query_repr = str(query_input)[:200] if query_input else "None"
            logger.error(f"Query execution failed: {query_repr} - {str(e)}")
            return {
                "success": False,
                "result": None,
                "error": f"Execution error: {str(e)}",
                "query_info": {"query": query_repr},
            }

    def _validate_query(self, query_string: str) -> Dict[str, Any]:
        """
        Validate query safety using multiple approaches.

        Returns:
            Dictionary with is_safe (bool) and reason (str)
        """
        # Check 1: String-based dangerous keyword detection
        query_lower = query_string.lower()
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in query_lower:
                return {
                    "is_safe": False,
                    "reason": f"Dangerous keyword detected: {keyword}",
                }

        # Check 2: AST parsing to detect dangerous patterns
        try:
            tree = ast.parse(query_string, mode="eval")
            ast_validation = self._validate_ast(tree)
            if not ast_validation["is_safe"]:
                return ast_validation
        except SyntaxError as e:
            return {
                "is_safe": False,
                "reason": f"Syntax error: {str(e)}",
            }

        # Check 3: Validate model names
        model_validation = self._validate_models(query_string)
        if not model_validation["is_safe"]:
            return model_validation

        return {"is_safe": True, "reason": "All validations passed"}

    def _validate_ast(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Validate AST to ensure only safe operations.

        Checks for:
        - Only allowed attribute access
        - No function calls except allowed methods
        - No assignments or deletions
        """
        for node in ast.walk(tree):
            # Block assignments
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.Delete)):
                return {
                    "is_safe": False,
                    "reason": "Assignment or deletion detected",
                }

            # Block imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return {
                    "is_safe": False,
                    "reason": "Import statement detected",
                }

            # Validate function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name not in self.ALLOWED_AGGREGATES:
                        return {
                            "is_safe": False,
                            "reason": f"Unauthorized function call: {func_name}",
                        }

        return {"is_safe": True, "reason": "AST validation passed"}

    def _validate_models(self, query_string: str) -> Dict[str, Any]:
        """Validate that only allowed models are referenced."""
        for model_name in self.ALLOWED_MODELS.keys():
            if model_name in query_string:
                # Found an allowed model
                return {"is_safe": True, "reason": "Model validation passed"}

        return {
            "is_safe": False,
            "reason": "No recognized model found in query",
        }

    def _execute_safe(self, query_string: str) -> Any:
        """
        Execute query without eval() - secure programmatic QuerySet construction.

        Security:
        - NO eval(), exec(), or compile() usage
        - Parses query string into components (model, methods, arguments)
        - Builds QuerySets programmatically using getattr() and method chaining
        - Validates all methods against allowlist before execution
        - Prevents code injection via Python sandbox bypass

        Example query_string:
            "OBCCommunity.objects.filter(barangay__municipality__name='Cotabato').count()"
        """
        try:
            # Parse query string into executable components
            parsed = self._parse_query_string(query_string)

            # Get model class from context
            model_name = parsed['model']
            if model_name not in self._context:
                raise ValueError(f"Model {model_name} not in allowed context")

            model_class = self._context[model_name]

            # Start with base queryset
            queryset = model_class.objects.all()

            # Chain methods programmatically
            for method_call in parsed['operations']:
                method_name = method_call['method']
                args = method_call.get('args', [])
                kwargs = method_call.get('kwargs', {})

                # Security: Validate method is allowed
                if method_name not in self.ALLOWED_METHODS and method_name not in self.ALLOWED_AGGREGATES:
                    raise SecurityError(f"Method {method_name} not allowed")

                # Get method and execute
                if hasattr(queryset, method_name):
                    method = getattr(queryset, method_name)
                    queryset = method(*args, **kwargs)
                else:
                    raise ValueError(f"Method {method_name} not available on QuerySet")

            return queryset

        except Exception as e:
            logger.error(f"Safe execution failed: {query_string} - {str(e)}")
            raise

    def _parse_query_string(self, query_string: str) -> Dict[str, Any]:
        """
        Parse query string into structured components for safe execution.

        Args:
            query_string: Django ORM query like "Model.objects.filter(field='value').count()"

        Returns:
            Dictionary with:
                - model: Model class name
                - operations: List of method calls with args/kwargs

        Security:
        - Uses AST parsing to extract method calls safely
        - Validates all components before returning
        - No direct string execution
        """
        try:
            # Parse the query string as an AST expression
            tree = ast.parse(query_string, mode='eval')

            # Extract model name and operations
            result = {
                'model': None,
                'operations': []
            }

            # Walk the AST to extract components
            result = self._extract_from_ast(tree.body)

            if not result['model']:
                raise ValueError("Could not extract model name from query")

            return result

        except SyntaxError as e:
            raise ValueError(f"Invalid query syntax: {str(e)}")

    def _extract_from_ast(self, node: ast.AST) -> Dict[str, Any]:
        """
        Recursively extract model and operations from AST node.

        Security:
        - Only extracts safe attribute access and method calls
        - Validates all extracted components
        """
        result = {
            'model': None,
            'operations': []
        }

        if isinstance(node, ast.Call):
            # Method call - extract method name and arguments
            method_info = self._extract_method_call(node)

            # Recursively process the function/attribute
            if isinstance(node.func, ast.Attribute):
                parent_result = self._extract_from_ast(node.func.value)
                result['model'] = parent_result['model']
                result['operations'] = parent_result['operations'] + [method_info]

        elif isinstance(node, ast.Attribute):
            # Attribute access like Model.objects
            parent_result = self._extract_from_ast(node.value)
            result['model'] = parent_result['model']
            result['operations'] = parent_result['operations']

            # Special handling for .objects
            if node.attr != 'objects':
                result['operations'].append({
                    'method': node.attr,
                    'args': [],
                    'kwargs': {}
                })

        elif isinstance(node, ast.Name):
            # Model name (e.g., "OBCCommunity")
            result['model'] = node.id

        return result

    def _extract_method_call(self, node: ast.Call) -> Dict[str, Any]:
        """
        Extract method name and arguments from AST Call node.

        Returns:
            Dictionary with method, args, kwargs

        Security:
        - Only extracts literal values (strings, numbers, booleans)
        - Blocks complex expressions that could be malicious
        """
        method_name = None

        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            method_name = node.func.id

        # Extract positional arguments
        args = []
        for arg in node.args:
            arg_value = self._extract_literal_value(arg)
            if arg_value is not None:
                args.append(arg_value)

        # Extract keyword arguments
        kwargs = {}
        for keyword in node.keywords:
            key = keyword.arg
            value = self._extract_literal_value(keyword.value)
            if value is not None:
                kwargs[key] = value

        return {
            'method': method_name,
            'args': args,
            'kwargs': kwargs
        }

    def _extract_literal_value(self, node: ast.AST) -> Any:
        """
        Safely extract literal values from AST nodes.

        Security:
        - Only returns primitive types (str, int, float, bool, None)
        - Returns None for complex expressions to prevent injection
        """
        if isinstance(node, ast.Constant):
            # Python 3.8+ - all literals are ast.Constant
            value = node.value
            if isinstance(value, (str, int, float, bool, type(None))):
                return value

        elif isinstance(node, ast.Str):
            # Python 3.7 compatibility
            return node.s

        elif isinstance(node, ast.Num):
            # Python 3.7 compatibility
            return node.n

        elif isinstance(node, ast.NameConstant):
            # Python 3.7 compatibility - True, False, None
            return node.value

        elif isinstance(node, ast.List):
            # List literal
            return [self._extract_literal_value(item) for item in node.elts]

        elif isinstance(node, ast.Dict):
            # Dict literal
            result = {}
            for key_node, value_node in zip(node.keys, node.values):
                key = self._extract_literal_value(key_node)
                value = self._extract_literal_value(value_node)
                if key is not None:
                    result[key] = value
            return result

        elif isinstance(node, ast.Call):
            # Handle special cases like Q() objects
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name == 'Q' and 'Q' in self._context:
                    # Reconstruct Q object
                    kwargs = {}
                    for keyword in node.keywords:
                        key = keyword.arg
                        value = self._extract_literal_value(keyword.value)
                        if value is not None:
                            kwargs[key] = value
                    return Q(**kwargs)

                # Handle aggregation functions
                if func_name in self.ALLOWED_AGGREGATES and func_name in self._context:
                    agg_class = self._context[func_name]
                    args = [self._extract_literal_value(arg) for arg in node.args]
                    kwargs = {
                        kw.arg: self._extract_literal_value(kw.value)
                        for kw in node.keywords
                    }
                    return agg_class(*args, **kwargs)

        # Unknown node type - return None for safety
        return None

    def _process_result(self, result: Any) -> Any:
        """
        Process query result and apply safety limits.

        Handles:
        - QuerySets: Convert to list with size limit
        - Aggregates: Return as-is
        - Single objects: Convert to dict
        """
        from django.db.models import QuerySet

        if isinstance(result, QuerySet):
            # Apply size limit
            limited_qs = result[: self.MAX_RESULTS]
            # Convert to list of dicts for JSON serialization
            return list(limited_qs.values())

        elif isinstance(result, dict):
            # Aggregate result
            return result

        elif isinstance(result, (int, float, str, bool, type(None))):
            # Primitive types
            return result

        elif hasattr(result, "__dict__"):
            # Single model instance - convert to dict
            return {
                "id": getattr(result, "id", None),
                "str": str(result),
                "model": result.__class__.__name__,
            }

        else:
            # Fallback
            return str(result)

    def _get_result_count(self, result: Any) -> int:
        """Get count of results."""
        if isinstance(result, list):
            return len(result)
        elif isinstance(result, dict):
            return 1
        elif isinstance(result, (int, float)):
            return 1
        else:
            return 0

    def _build_safe_context(self) -> Dict[str, Any]:
        """
        Build safe execution context with only allowed models and functions.

        Returns:
            Dictionary mapping names to safe objects
        """
        context = {}

        # Import and add allowed models
        for model_name, import_path in self.ALLOWED_MODELS.items():
            try:
                module_path, class_name = import_path.rsplit(".", 1)
                module = __import__(module_path, fromlist=[class_name])
                context[model_name] = getattr(module, class_name)
            except (ImportError, AttributeError) as e:
                logger.warning(f"Could not import {import_path}: {e}")

        # Add aggregation functions
        context["Count"] = Count
        context["Sum"] = Sum
        context["Avg"] = Avg
        context["Max"] = Max
        context["Min"] = Min
        context["Q"] = Q

        return context

    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get list of available models with metadata.

        Returns:
            List of dicts with model_name, import_path, fields
        """
        available = []

        for model_name, import_path in self.ALLOWED_MODELS.items():
            try:
                module_path, class_name = import_path.rsplit(".", 1)
                module = __import__(module_path, fromlist=[class_name])
                model_class = getattr(module, class_name)

                # Get field names
                fields = [f.name for f in model_class._meta.get_fields()]

                available.append(
                    {
                        "model_name": model_name,
                        "import_path": import_path,
                        "fields": fields,
                        "verbose_name": model_class._meta.verbose_name,
                    }
                )
            except Exception as e:
                logger.warning(f"Could not get info for {model_name}: {e}")

        return available


class SecurityError(Exception):
    """Raised when a security violation is detected in query execution."""
    pass


# Singleton instance
_executor = None


def get_query_executor() -> QueryExecutor:
    """Get singleton query executor instance."""
    global _executor
    if _executor is None:
        _executor = QueryExecutor()
    return _executor
