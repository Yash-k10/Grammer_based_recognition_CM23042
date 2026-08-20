"""
Phase 1 Test Suite — Formal Grammar Parsing & Tokenization Verification
"""

import sys
from lexer import Lexer
from parser import Parser


def run_tests():
    lexer = Lexer()
    parser = Parser()

    test_cases = [
        # (input_string, expected_validity, test_label)
        ("dhanshree01@gmail.com", True, "Standard valid email"),
        ("john.doe@company.org", True, "Dot-separated local part"),
        ("user_123@sub-domain.co.in", True, "Underscore, hyphen domain"),
        ("test.name+tag@dev.io", True, "Plus separator in local part"),
        
        ("plainaddress", False, "Missing '@' separator"),
        ("@missinglocal.com", False, "Missing local part before '@'"),
        ("user@.com", False, "Missing domain name before '.'"),
        ("user@domain", False, "Missing top-level domain (TLD)"),
        ("user@@domain.com", False, "Multiple '@' symbols"),
        ("user name@gmail.com", False, "Invalid space character"),
    ]

    print("=" * 65)
    print("      GRAMMAR-BASED PATTERN RECOGNITION — PHASE 1 TEST SUITE      ")
    print("=" * 65)

    passed_count = 0
    total_count = len(test_cases)

    for i, (inp, expected, label) in enumerate(test_cases, 1):
        tokens = lexer.tokenize(inp)
        res = parser.parse(tokens)

        passed = (res.is_valid == expected)
        if passed:
            passed_count += 1
            status_str = "[PASS]"
        else:
            status_str = "[FAIL]"

        print(f"\nTest {i:02d}: {status_str} - {label}")
        print(f"  Input:    '{inp}'")
        print(f"  Expected: {'ACCEPTED' if expected else 'REJECTED'}")
        print(f"  Actual:   {'ACCEPTED' if res.is_valid else 'REJECTED'}")

        if res.is_valid:
            print(f"  Matched:  {res.matched_components}")
        else:
            print(f"  Reason:   {res.error_message}")

    print("\n" + "=" * 65)
    print(f"SUMMARY: {passed_count}/{total_count} tests passed ({passed_count/total_count*100:.1f}% accuracy)")
    print("=" * 65)

    if passed_count != total_count:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
