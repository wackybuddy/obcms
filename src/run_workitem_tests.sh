#!/bin/bash

# Script to run WorkItem integration tests
# Usage: ./run_workitem_tests.sh

echo "======================================================================="
echo "OBCMS WorkItem Integration Test Suite"
echo "======================================================================="
echo ""
echo "Running comprehensive workitem integration tests..."
echo ""

# Run tests without coverage for faster execution
/Users/saidamenmambayao/apps/obcms/venv/bin/pytest \
    budget_execution/tests/test_workitem_integration.py \
    -v \
    --tb=short \
    --no-cov \
    --strict-markers \
    -m "integration" \
    2>&1 | tee workitem_test_results.txt

# Print summary
echo ""
echo "======================================================================="
echo "Test Execution Complete"
echo "======================================================================="
echo ""
echo "Results saved to: workitem_test_results.txt"
echo ""
