#!/bin/bash
# WorkItem E2E Test Runner Script
# Runs all workitem-related tests and captures results

set -e

cd /Users/saidamenmambayao/apps/obcms/src

# Source virtual environment
source /Users/saidamenmambayao/apps/obcms/venv/bin/activate

# Create test output directory
mkdir -p test_results

# Test 1: E2E Tests (skipped - requires live server)
echo "==============================================="
echo "TEST 1: Playwright E2E Tests"
echo "==============================================="
echo "Status: SKIPPED (requires RUN_PLAYWRIGHT_E2E=1)"
python -m pytest common/tests/test_e2e_workitem.py --collect-only -q 2>&1 | tail -5

# Test 2: WorkItem Integration Tests
echo ""
echo "==============================================="
echo "TEST 2: WorkItem Integration Tests"
echo "==============================================="
python -m pytest common/tests/test_work_item_integration.py -v --tb=line --timeout=30 2>&1 | tee test_results/integration_tests.log || true

# Test 3: WorkItem Delete Tests
echo ""
echo "==============================================="
echo "TEST 3: WorkItem Delete Tests"
echo "==============================================="
python -m pytest common/tests/test_work_item_delete.py -v --tb=line --timeout=30 2>&1 | tee test_results/delete_tests.log || true

# Test 4: WorkItem Views Tests
echo ""
echo "==============================================="
echo "TEST 4: WorkItem Views Tests"
echo "==============================================="
python -m pytest common/tests/test_work_item_views.py -v --tb=line --timeout=30 2>&1 | tee test_results/views_tests.log || true

# Test 5: WorkItem Calendar Tests
echo ""
echo "==============================================="
echo "TEST 5: WorkItem Calendar Tests"
echo "==============================================="
python -m pytest common/tests/test_work_item_calendar.py -v --tb=line --timeout=30 2>&1 | tee test_results/calendar_tests.log || true

echo ""
echo "==============================================="
echo "TEST SUMMARY"
echo "==============================================="
echo "Test logs saved to: test_results/"
ls -lh test_results/ 2>/dev/null || echo "No test results generated"

echo ""
echo "Done!"
