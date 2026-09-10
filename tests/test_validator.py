"""
Unit Tests for PatternValidator Module (validator.py).
Validates end-to-end verdict evaluation, error classification, visual rendering, and batch processing.
"""

import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from validator import PatternValidator, ValidationResult


class TestValidator(unittest.TestCase):

    def setUp(self):
        self.output_dir = "test_output"
        self.validator = PatternValidator(grammar_path="grammar/email.cfg", output_dir=self.output_dir)

    def test_verdict_accepted(self):
        res = self.validator.validate("dhanshree01@gmail.com")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.verdict, "ACCEPTED")
        self.assertIsNone(res.error_code)
        self.assertIn("local", res.matched_components)

    def test_error_classification_empty(self):
        res = self.validator.validate("")
        self.assertFalse(res.is_valid)
        self.assertEqual(res.verdict, "REJECTED")
        self.assertEqual(res.error_code, "EMPTY_INPUT")

    def test_error_classification_lexical(self):
        res = self.validator.validate("user name@domain.com")
        self.assertFalse(res.is_valid)
        self.assertEqual(res.verdict, "REJECTED")
        self.assertEqual(res.error_code, "LEXICAL_ERROR")

    def test_error_classification_structural(self):
        res = self.validator.validate("plainaddress.com")
        self.assertFalse(res.is_valid)
        self.assertEqual(res.verdict, "REJECTED")
        self.assertEqual(res.error_code, "STRUCTURAL_ERROR")

    def test_error_classification_derivation_syntax(self):
        res = self.validator.validate("@missinglocal.com")
        self.assertFalse(res.is_valid)
        self.assertEqual(res.verdict, "REJECTED")
        self.assertEqual(res.error_code, "DERIVATION_SYNTAX_ERROR")

    def test_visual_artifact_generation(self):
        res = self.validator.validate("test@visual.org", generate_visuals=True, file_prefix="unit_test_vis")
        self.assertTrue(res.is_valid)
        self.assertIsNotNone(res.dot_file)
        self.assertTrue(os.path.exists(res.dot_file))
        self.assertIsNotNone(res.svg_file)
        self.assertTrue(os.path.exists(res.svg_file))
        self.assertIsNotNone(res.ascii_tree)

    def test_json_serialization(self):
        res = self.validator.validate("serialize@json.dev")
        d = res.to_dict()
        self.assertEqual(d["verdict"], "ACCEPTED")
        self.assertEqual(d["input"], "serialize@json.dev")
        json_str = json.dumps(d)
        self.assertTrue(len(json_str) > 0)

    def test_batch_validation(self):
        inputs = ["valid1@gmail.com", "invalid_email", "valid2@org.net"]
        results = self.validator.validate_batch(inputs)
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0].is_valid)
        self.assertFalse(results[1].is_valid)
        self.assertTrue(results[2].is_valid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
