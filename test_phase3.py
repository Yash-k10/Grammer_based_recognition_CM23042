"""
Phase 3 Test Suite — Quality Assurance, Grammar Extensibility & Benchmarking Verification
"""

import sys
import os
import time
from validator import PatternValidator

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def run_phase3_tests():
    print("=" * 72)
    print("     GRAMMAR-BASED PATTERN RECOGNITION — PHASE 3 QA TEST SUITE       ")
    print("=" * 72)

    test_out = "test_output"
    os.makedirs(test_out, exist_ok=True)
    email_val = PatternValidator(grammar_path="grammar/email.cfg", output_dir=test_out)
    date_val = PatternValidator(grammar_path="grammar/date.cfg", output_dir=test_out)

    passed_count = 0
    total_count = 0

    # -------------------------------------------------------------
    # 1. Primary Grammar (Email) QA Matrix
    # -------------------------------------------------------------
    print("\n--- 1. Primary Grammar (Email) QA Tests ---")
    email_cases = [
        ("dhanshree01@gmail.com", True, "ACCEPTED", None, "Standard email"),
        ("first.last@university.edu", True, "ACCEPTED", None, "Dot in local"),
        ("dev+alert_99@cloud-tech.io", True, "ACCEPTED", None, "Complex local & hyphen domain"),
        ("admin@portal.state.gov.in", True, "ACCEPTED", None, "Multi-level government domain"),
        ("", False, "REJECTED", "EMPTY_INPUT", "Empty email string"),
        ("invalid char@domain.com", False, "REJECTED", "LEXICAL_ERROR", "Space in local"),
        ("user!name@domain.com", False, "REJECTED", "LEXICAL_ERROR", "Exclamation in local"),
        ("no_at_sign.org", False, "REJECTED", "STRUCTURAL_ERROR", "Missing @ sign"),
        ("user@@domain.com", False, "REJECTED", "STRUCTURAL_ERROR", "Double @ sign"),
        ("@nodomain.com", False, "REJECTED", "DERIVATION_SYNTAX_ERROR", "Missing local part"),
        ("user@domain", False, "REJECTED", "DERIVATION_SYNTAX_ERROR", "Missing TLD / dot"),
    ]

    for inp, exp_valid, exp_verdict, exp_code, desc in email_cases:
        total_count += 1
        res = email_val.validate(inp)
        ok = (res.is_valid == exp_valid) and (res.verdict == exp_verdict) and (exp_code is None or res.error_code == exp_code)
        if ok:
            passed_count += 1
            st = "[PASS]"
        else:
            st = "[FAIL]"
        print(f"Test {total_count:02d}: {st} - {desc} -> {res.verdict} ({res.error_code or 'OK'})")

    # -------------------------------------------------------------
    # 2. Secondary Grammar (Date) Extensibility QA Matrix
    # -------------------------------------------------------------
    print("\n--- 2. Secondary Grammar (Date Extensibility) QA Tests ---")
    date_cases = [
        ("2026-09-10", True, "ACCEPTED", None, "ISO YYYY-MM-DD dash"),
        ("2025/12/31", True, "ACCEPTED", None, "ISO YYYY/MM/DD slash"),
        ("2024.07.04", True, "ACCEPTED", None, "ISO YYYY.MM.DD dot"),
        ("15/08/1947", True, "ACCEPTED", None, "European DD/MM/YYYY slash"),
        ("26-01-1950", True, "ACCEPTED", None, "European DD-MM-YYYY dash"),
        ("2024-02-29", True, "ACCEPTED", None, "Leap year Feb 29 (Valid)"),
        ("2023-02-29", False, "REJECTED", "DERIVATION_SYNTAX_ERROR", "Non-leap year Feb 29 (Invalid)"),
        ("2026-13-01", False, "REJECTED", "DERIVATION_SYNTAX_ERROR", "Invalid month 13"),
        ("32/05/2026", False, "REJECTED", "DERIVATION_SYNTAX_ERROR", "Invalid day 32"),
        ("2026-09/10", False, "REJECTED", "DERIVATION_SYNTAX_ERROR", "Mismatched separators (- and /)"),
        ("20260910", False, "REJECTED", "STRUCTURAL_ERROR", "Missing date separators"),
        ("2026-09-10-11", False, "REJECTED", "STRUCTURAL_ERROR", "Extra date separators"),
        ("2026-09-10#abc", False, "REJECTED", "LEXICAL_ERROR", "Invalid lexical characters in date"),
    ]

    for inp, exp_valid, exp_verdict, exp_code, desc in date_cases:
        total_count += 1
        res = date_val.validate(inp)
        ok = (res.is_valid == exp_valid) and (res.verdict == exp_verdict) and (exp_code is None or res.error_code == exp_code)
        if ok:
            passed_count += 1
            st = "[PASS]"
        else:
            st = "[FAIL]"
        print(f"Test {total_count:02d}: {st} - {desc} -> {res.verdict} ({res.error_code or 'OK'})")

    # -------------------------------------------------------------
    # 3. Visual Artifact Generation Verification
    # -------------------------------------------------------------
    print("\n--- 3. Visual Parse Tree Artifact Verification ---")
    total_count += 1
    email_vis = email_val.validate("dhanshree01@gmail.com", generate_visuals=True, file_prefix="phase3_email")
    if email_vis.svg_file and os.path.exists(email_vis.svg_file) and email_vis.dot_file and os.path.exists(email_vis.dot_file):
        passed_count += 1
        print(f"Test {total_count:02d}: [PASS] - Email SVG & DOT artifacts generated successfully")
    else:
        print(f"Test {total_count:02d}: [FAIL] - Email visual generation failed")

    total_count += 1
    date_vis = date_val.validate("2026-09-10", generate_visuals=True, file_prefix="phase3_date")
    if date_vis.svg_file and os.path.exists(date_vis.svg_file) and date_vis.dot_file and os.path.exists(date_vis.dot_file):
        passed_count += 1
        print(f"Test {total_count:02d}: [PASS] - Date SVG & DOT artifacts generated successfully")
    else:
        print(f"Test {total_count:02d}: [FAIL] - Date visual generation failed")

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    acc = (passed_count / total_count) * 100
    print("\n" + "=" * 72)
    print(f"PHASE 3 TEST SUMMARY: {passed_count}/{total_count} passed ({acc:.1f}% accuracy)")
    print("=" * 72)

    if passed_count != total_count:
        sys.exit(1)


if __name__ == "__main__":
    run_phase3_tests()
