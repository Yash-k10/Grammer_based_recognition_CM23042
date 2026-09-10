"""
Unified Test Runner for Grammar-Based Pattern Recognition Engine.
Executes all unit tests in tests/ directory and prints aggregated test statistics.
"""

import unittest
import sys
import os
import time

# Ensure proper encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_test_suite():
    print("=" * 70)
    print("    GRAMMAR-BASED PATTERN RECOGNITION — AUTOMATED QA TEST SUITE    ")
    print("=" * 70)

    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern="test_*.py")

    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - start_time

    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    accuracy = (passed / total_tests * 100) if total_tests > 0 else 0.0

    print("\n" + "=" * 70)
    print("                      TEST SUITE SUMMARY                      ")
    print("=" * 70)
    print(f"Total Tests Executed: {total_tests}")
    print(f"Passed:               {passed}")
    print(f"Failures:             {failures}")
    print(f"Errors:               {errors}")
    print(f"Overall Accuracy:     {accuracy:.1f}%")
    print(f"Execution Time:       {elapsed:.3f} seconds")
    print("=" * 70)

    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    run_test_suite()
