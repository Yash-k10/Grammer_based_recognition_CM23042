"""
Unit Tests for Benchmark Module (benchmark.py).
Validates synthetic generator, benchmark execution, and linear regression calculations.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from benchmark import generate_synthetic_email, run_benchmark


class TestBenchmark(unittest.TestCase):

    def test_synthetic_generator_length(self):
        sample = generate_synthetic_email(50)
        self.assertGreaterEqual(len(sample), 40)
        self.assertIn("@domain-corp.org", sample)

    def test_run_benchmark_lightweight(self):
        # Quick benchmark with small scales and iterations
        scales = [20, 50, 100]
        report = run_benchmark(scales, iterations=10)
        
        self.assertEqual(len(report["results"]), 3)
        self.assertIn("complexity_analysis", report)
        self.assertIn("r_squared", report["complexity_analysis"])
        self.assertTrue(report["complexity_analysis"]["r_squared"] > 0.8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
