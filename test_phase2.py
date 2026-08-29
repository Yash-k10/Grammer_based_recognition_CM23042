"""
Phase 2 Test Suite — Validation Engine, Parse Tree Visualization & CLI Pipeline Verification
"""

import sys
import os
import json
from validator import PatternValidator, ValidationResult
from visualize import ParseTreeVisualizer


def run_phase2_tests():
    print("=" * 70)
    print("     GRAMMAR-BASED PATTERN RECOGNITION — PHASE 2 TEST SUITE       ")
    print("=" * 70)

    test_output_dir = "test_output"
    validator = PatternValidator(output_dir=test_output_dir)
    passed_count = 0
    total_count = 0

    # -------------------------------------------------------------
    # 1. Validation Verdict & Error Classification Tests
    # -------------------------------------------------------------
    test_cases = [
        # (input, expected_valid, expected_verdict, expected_error_code, description)
        ("dhanshree01@gmail.com", True, "ACCEPTED", None, "Standard valid email"),
        ("first.last@university.edu", True, "ACCEPTED", None, "Dot in username"),
        ("dev_team+alerts@tech-corp.org", True, "ACCEPTED", None, "Plus & underscore in username, hyphen domain"),
        ("admin@sub.domain.co.in", True, "ACCEPTED", None, "Multi-level subdomain"),
        
        ("", False, "REJECTED", "EMPTY_INPUT", "Empty string input"),
        ("user space@gmail.com", False, "REJECTED", "LEXICAL_ERROR", "Invalid whitespace character"),
        ("user#name@domain.com", False, "REJECTED", "LEXICAL_ERROR", "Invalid symbol # in local"),
        ("noatsign.com", False, "REJECTED", "STRUCTURAL_ERROR", "Missing @ symbol"),
        ("user@@domain.com", False, "REJECTED", "STRUCTURAL_ERROR", "Double @ symbol"),
        ("@nodomain.com", False, "REJECTED", "DERIVATION_SYNTAX_ERROR", "Missing local part"),
        ("user@", False, "REJECTED", "DERIVATION_SYNTAX_ERROR", "Missing domain part"),
        ("user@domain", False, "REJECTED", "DERIVATION_SYNTAX_ERROR", "Missing TLD / dot"),
        ("user@.com", False, "REJECTED", "DERIVATION_SYNTAX_ERROR", "Empty domain label"),
        (".user@domain.com", False, "REJECTED", "DERIVATION_SYNTAX_ERROR", "Leading separator in local part"),
    ]

    print("\n--- 1. Validation Verdict & Error Classification Tests ---")
    for i, (inp, exp_valid, exp_verdict, exp_err_code, desc) in enumerate(test_cases, 1):
        total_count += 1
        res = validator.validate(inp)
        
        valid_ok = (res.is_valid == exp_valid)
        verdict_ok = (res.verdict == exp_verdict)
        error_ok = (exp_err_code is None) or (res.error_code == exp_err_code)

        passed = valid_ok and verdict_ok and error_ok
        if passed:
            passed_count += 1
            status = "[PASS]"
        else:
            status = "[FAIL]"

        print(f"Test {i:02d}: {status} - {desc}")
        print(f"  Input:    '{inp}'")
        print(f"  Verdict:  {res.verdict} (Expected: {exp_verdict})")
        if not res.is_valid:
            print(f"  ErrCode:  {res.error_code} (Expected: {exp_err_code})")
            print(f"  Message:  {res.error_message}")
        else:
            print(f"  Matched:  {res.matched_components}")

    # -------------------------------------------------------------
    # 2. Visualizer Generation & Artifact File Verification
    # -------------------------------------------------------------
    print("\n--- 2. Parse Tree Visualizer Artifact Verification ---")
    sample_pattern = "dhanshree01@gmail.com"
    vis_res = validator.validate(sample_pattern, generate_visuals=True, file_prefix="test_email")

    total_count += 1
    if vis_res.dot_file and os.path.exists(vis_res.dot_file):
        print(f"Test {total_count:02d}: [PASS] - DOT file generated: {vis_res.dot_file}")
        passed_count += 1
    else:
        print(f"Test {total_count:02d}: [FAIL] - DOT file missing")

    total_count += 1
    if vis_res.svg_file and os.path.exists(vis_res.svg_file):
        print(f"Test {total_count:02d}: [PASS] - Standalone SVG generated: {vis_res.svg_file}")
        passed_count += 1
    else:
        print(f"Test {total_count:02d}: [FAIL] - Standalone SVG missing")

    total_count += 1
    if vis_res.ascii_tree and "EMAIL" in vis_res.ascii_tree:
        print(f"Test {total_count:02d}: [PASS] - Unicode ASCII tree generated")
        passed_count += 1
    else:
        print(f"Test {total_count:02d}: [FAIL] - ASCII tree generation failed")

    # -------------------------------------------------------------
    # 3. JSON Serialization & Batch Processing Test
    # -------------------------------------------------------------
    print("\n--- 3. JSON Serialization & Batch Verification ---")
    total_count += 1
    batch_inputs = ["user1@test.com", "bad_pattern", "user2@sub.domain.org"]
    batch_results = validator.validate_batch(batch_inputs)
    
    if len(batch_results) == 3 and batch_results[0].is_valid and not batch_results[1].is_valid and batch_results[2].is_valid:
        print(f"Test {total_count:02d}: [PASS] - Batch processing (3 inputs) succeeded")
        passed_count += 1
    else:
        print(f"Test {total_count:02d}: [FAIL] - Batch processing incorrect")

    total_count += 1
    json_dict = vis_res.to_dict()
    json_str = json.dumps(json_dict)
    if "verdict" in json_dict and json_dict["verdict"] == "ACCEPTED" and "visual_artifacts" in json_dict:
        print(f"Test {total_count:02d}: [PASS] - JSON Serialization structured properly")
        passed_count += 1
    else:
        print(f"Test {total_count:02d}: [FAIL] - JSON Serialization mismatch")

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    acc = (passed_count / total_count) * 100
    print(f"PHASE 2 TEST SUMMARY: {passed_count}/{total_count} passed ({acc:.1f}% accuracy)")
    print("=" * 70)

    if passed_count != total_count:
        sys.exit(1)


if __name__ == "__main__":
    run_phase2_tests()
