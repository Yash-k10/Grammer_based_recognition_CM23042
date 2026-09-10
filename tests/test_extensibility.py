"""
Unit Tests for Grammar Extensibility Proof (grammar/date.cfg).
Validates that the recognition engine seamlessly supports secondary pattern grammars without core rewrites.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from validator import PatternValidator


class TestGrammarExtensibility(unittest.TestCase):

    def setUp(self):
        self.output_dir = "test_output"
        self.date_validator = PatternValidator(
            grammar_path="grammar/date.cfg",
            output_dir=self.output_dir
        )

    # --- Valid Date Acceptance Tests ---
    def test_iso_date_dash_accepted(self):
        res = self.date_validator.validate("2026-09-10")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.verdict, "ACCEPTED")
        self.assertEqual(res.matched_components["year"], "2026")
        self.assertEqual(res.matched_components["month"], "09")
        self.assertEqual(res.matched_components["day"], "10")
        self.assertEqual(res.matched_components["format"], "YYYY-MM-DD")

    def test_iso_date_slash_accepted(self):
        res = self.date_validator.validate("2025/12/31")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.matched_components["format"], "YYYY/MM/DD")

    def test_iso_date_dot_accepted(self):
        res = self.date_validator.validate("2024.01.15")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.matched_components["format"], "YYYY.MM.DD")

    def test_standard_date_slash_accepted(self):
        res = self.date_validator.validate("15/08/1947")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.matched_components["day"], "15")
        self.assertEqual(res.matched_components["month"], "08")
        self.assertEqual(res.matched_components["year"], "1947")
        self.assertEqual(res.matched_components["format"], "DD/MM/YYYY")

    def test_standard_date_dash_accepted(self):
        res = self.date_validator.validate("26-01-1950")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.matched_components["format"], "DD-MM-YYYY")

    def test_leap_year_february_29(self):
        # 2024 is a leap year -> Valid
        res_leap = self.date_validator.validate("2024-02-29")
        self.assertTrue(res_leap.is_valid)

        # 2023 is not a leap year -> Rejected
        res_non_leap = self.date_validator.validate("2023-02-29")
        self.assertFalse(res_non_leap.is_valid)
        self.assertEqual(res_non_leap.error_code, "DERIVATION_SYNTAX_ERROR")

    # --- Invalid Date Rejection Tests ---
    def test_out_of_range_month(self):
        res = self.date_validator.validate("2026-13-10")
        self.assertFalse(res.is_valid)
        self.assertEqual(res.verdict, "REJECTED")
        self.assertIn("Month", res.error_message)

    def test_out_of_range_day(self):
        res = self.date_validator.validate("32/01/2026")
        self.assertFalse(res.is_valid)
        self.assertEqual(res.verdict, "REJECTED")
        self.assertIn("Day", res.error_message)

    def test_mismatched_separators(self):
        res = self.date_validator.validate("2026-09/10")
        self.assertFalse(res.is_valid)
        self.assertEqual(res.verdict, "REJECTED")
        self.assertIn("Mismatched", res.error_message)

    def test_missing_separator(self):
        res = self.date_validator.validate("20260910")
        self.assertFalse(res.is_valid)
        self.assertEqual(res.verdict, "REJECTED")
        self.assertEqual(res.error_code, "STRUCTURAL_ERROR")

    def test_extra_separator(self):
        res = self.date_validator.validate("2026-09-10-01")
        self.assertFalse(res.is_valid)
        self.assertEqual(res.verdict, "REJECTED")

    def test_date_visual_tree_generation(self):
        res = self.date_validator.validate("2026-09-10", generate_visuals=True, file_prefix="date_ext_test")
        self.assertTrue(res.is_valid)
        self.assertIsNotNone(res.svg_file)
        self.assertTrue(os.path.exists(res.svg_file))
        self.assertIn("DATE", res.ascii_tree)


if __name__ == "__main__":
    unittest.main(verbosity=2)
