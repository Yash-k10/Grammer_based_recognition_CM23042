"""
Unit Tests for Lexer Module (lexer.py).
Validates tokenization accuracy, token positioning, TLD recognition, and error handling.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import Lexer, Token


class TestLexer(unittest.TestCase):

    def setUp(self):
        self.email_lexer = Lexer(grammar_type="email")
        self.date_lexer = Lexer(grammar_type="date")

    # --- Email Tokenization Tests ---
    def test_standard_email_tokens(self):
        sample = "dhanshree01@gmail.com"
        tokens = self.email_lexer.tokenize(sample)
        
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[0].type, "WORD")
        self.assertEqual(tokens[0].value, "dhanshree01")
        self.assertEqual(tokens[1].type, "AT")
        self.assertEqual(tokens[2].type, "WORD")
        self.assertEqual(tokens[2].value, "gmail")
        self.assertEqual(tokens[3].type, "DOT")
        self.assertEqual(tokens[4].type, "TLD")
        self.assertEqual(tokens[4].value, "com")

    def test_local_part_separators(self):
        sample = "john.doe+filter_1@company.org"
        tokens = self.email_lexer.tokenize(sample)
        
        types = [t.type for t in tokens]
        self.assertIn("SEP", types)
        self.assertIn("AT", types)
        self.assertIn("TLD", types)

    def test_domain_subdomains_and_hyphens(self):
        sample = "user@mail-server.sub.co.in"
        tokens = self.email_lexer.tokenize(sample)
        
        values = [t.value for t in tokens]
        self.assertIn("@", values)
        self.assertIn("-", values)
        self.assertIn(".", values)
        self.assertIn("in", values)

    def test_empty_and_invalid_inputs(self):
        self.assertEqual(self.email_lexer.tokenize(""), [])
        self.assertEqual(self.email_lexer.tokenize(None), [])

    def test_invalid_characters_detected(self):
        sample = "user name#tag@domain.com"
        tokens = self.email_lexer.tokenize(sample)
        invalid_tokens = [t for t in tokens if t.type == "INVALID"]
        self.assertGreaterEqual(len(invalid_tokens), 1)

    # --- Date Tokenization Tests ---
    def test_date_iso_tokens(self):
        sample = "2026-09-10"
        tokens = self.date_lexer.tokenize(sample)
        
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[0].type, "DIGIT4")
        self.assertEqual(tokens[0].value, "2026")
        self.assertEqual(tokens[1].type, "SEP")
        self.assertEqual(tokens[1].value, "-")
        self.assertEqual(tokens[2].type, "DIGIT2")
        self.assertEqual(tokens[2].value, "09")
        self.assertEqual(tokens[3].type, "SEP")
        self.assertEqual(tokens[4].type, "DIGIT2")
        self.assertEqual(tokens[4].value, "10")

    def test_date_standard_tokens(self):
        sample = "15/08/1947"
        tokens = self.date_lexer.tokenize(sample)
        
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[0].type, "DIGIT2")
        self.assertEqual(tokens[0].value, "15")
        self.assertEqual(tokens[1].type, "SEP")
        self.assertEqual(tokens[1].value, "/")
        self.assertEqual(tokens[2].type, "DIGIT2")
        self.assertEqual(tokens[2].value, "08")
        self.assertEqual(tokens[3].type, "SEP")
        self.assertEqual(tokens[4].type, "DIGIT4")
        self.assertEqual(tokens[4].value, "1947")

    def test_date_invalid_characters(self):
        sample = "2026-09-10#abc"
        tokens = self.date_lexer.tokenize(sample)
        invalid_toks = [t for t in tokens if t.type == "INVALID"]
        self.assertTrue(len(invalid_toks) > 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
