"""
Unit Tests for Parser Module (parser.py).
Validates Context-Free Grammar derivation, ParseTreeNode structures, and syntax error detections.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import Lexer
from parser import Parser, ParseTreeNode, ParseResult


class TestParser(unittest.TestCase):

    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser("grammar/email.cfg")

    # --- ParseTreeNode Tests ---
    def test_parse_tree_node_structure(self):
        leaf = ParseTreeNode(symbol="DIGIT", value="5")
        self.assertTrue(leaf.is_leaf())
        self.assertEqual(leaf.to_dict(), {"symbol": "DIGIT", "value": "5"})

        parent = ParseTreeNode(symbol="NUMBER", children=[leaf])
        self.assertFalse(parent.is_leaf())
        self.assertEqual(len(parent.children), 1)
        self.assertIn("NUMBER", parent.pretty_print())

    # --- Derivation Acceptance Tests ---
    def test_valid_derivation(self):
        tokens = self.lexer.tokenize("dhanshree01@gmail.com")
        result = self.parser.parse(tokens)

        self.assertTrue(result.is_valid)
        self.assertIsNotNone(result.parse_tree)
        self.assertEqual(result.parse_tree.symbol, "EMAIL")
        self.assertEqual(result.matched_components["local"], "dhanshree01")
        self.assertEqual(result.matched_components["domain"], "gmail")
        self.assertEqual(result.matched_components["tld"], "com")

    def test_complex_email_derivation(self):
        tokens = self.lexer.tokenize("user.name+tag@sub-corp.co.in")
        result = self.parser.parse(tokens)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.matched_components["tld"], "in")

    # --- Derivation Rejection Tests ---
    def test_missing_at_symbol(self):
        tokens = self.lexer.tokenize("plainaddress.com")
        result = self.parser.parse(tokens)

        self.assertFalse(result.is_valid)
        self.assertIn("Missing '@'", result.error_message)

    def test_multiple_at_symbols(self):
        tokens = self.lexer.tokenize("user@@domain.com")
        result = self.parser.parse(tokens)

        self.assertFalse(result.is_valid)
        self.assertIn("Multiple '@'", result.error_message)

    def test_missing_local_part(self):
        tokens = self.lexer.tokenize("@domain.com")
        result = self.parser.parse(tokens)

        self.assertFalse(result.is_valid)
        self.assertIn("Local part", result.error_message)

    def test_missing_domain_part(self):
        tokens = self.lexer.tokenize("user@")
        result = self.parser.parse(tokens)

        self.assertFalse(result.is_valid)
        self.assertIn("Domain part", result.error_message)

    def test_missing_tld(self):
        tokens = self.lexer.tokenize("user@domain")
        result = self.parser.parse(tokens)

        self.assertFalse(result.is_valid)
        self.assertIn("TLD", result.error_message)

    def test_empty_tokens(self):
        result = self.parser.parse([])
        self.assertFalse(result.is_valid)
        self.assertIn("Empty token stream", result.error_message)


if __name__ == "__main__":
    unittest.main(verbosity=2)
