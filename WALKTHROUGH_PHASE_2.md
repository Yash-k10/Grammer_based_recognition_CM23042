# Phase 2 Walkthrough — Validation Engine, Visualization & CLI Pipeline

**Project Title:** Grammar-Based Pattern Recognition Engine  
**Phase Completed:** Phase 2 — Validation Engine, Visualization & CLI Pipeline  
**Accuracy Score:** 100% (19/19 Test Cases Passed)  

---

## 🎯 Phase 2 Objectives & Achievements

In Phase 2, we built the **Validation Engine**, **Multi-Format Parse Tree Visualizer**, and **Unified CLI Pipeline**, connecting the Phase 1 lexer and parser into an end-to-end usable tool.

---

## 🛠️ Key Components Delivered

```
grammar_based Recognition/
├── grammar/
│   └── email.cfg         # Formal CFG / BNF rules
├── lexer.py              # Regex tokenizer & terminal matching
├── parser.py             # LL(1) recursive-descent parser
├── visualize.py          # DOT, SVG, ASCII tree visualizer (NEW)
├── validator.py          # Verdict logic, error classifier & CLI (NEW)
├── test_phase1.py        # Phase 1 test suite
├── test_phase2.py        # Phase 2 test suite (19/19 passing) (NEW)
├── samples.txt           # Batch test dataset (NEW)
└── output/               # Rendered SVG and DOT trees (NEW)
```

---

### 1. Parse Tree Visualizer (`visualize.py`)
* **File:** [`visualize.py`](file:///d:/yash/pattern_recognition/grammar_based%20Recognition/visualize.py)
* **Features:**
  * **Graphviz DOT Generation (`generate_dot`, `save_dot`):** Generates `.dot` graph scripts with custom palette for Root (Indigo), Non-terminals (Blue), and Terminals (Emerald).
  * **Pure-Python Standalone SVG (`render_svg`):** Renders high-quality vector diagrams with gradient background, rounded badges, drop shadows, and connectors—requires zero external binary dependencies.
  * **Unicode Terminal Tree (`render_ascii`):** Formats parse trees using clean box-drawing connectors directly in CLI output.
  * **Graphviz Render (`render_graphviz`):** Optional PNG/PDF rendering via Graphviz when system `dot` is present.

---

### 2. Validation Engine & Pipeline (`validator.py`)
* **File:** [`validator.py`](file:///d:/yash/pattern_recognition/grammar_based%20Recognition/validator.py)
* **Features:**
  * **Structured Verdict Logic:** Emits explicit `ACCEPTED` or `REJECTED` verdicts.
  * **Categorized Error Diagnostics:** Classifies rejections into:
    * `EMPTY_INPUT`
    * `LEXICAL_ERROR`
    * `STRUCTURAL_ERROR`
    * `DERIVATION_SYNTAX_ERROR`
  * **Sub-Pattern Extraction:** Extracts matched dictionary components (`local`, `domain`, `tld`, `full`).
  * **Unified CLI Interface:**
    * Single pattern: `python validator.py --input "dhanshree01@gmail.com" --visualize`
    * JSON output: `python validator.py --input "dhanshree01@gmail.com" --format json`
    * Tree output: `python validator.py --input "dhanshree01@gmail.com" --format tree`
    * Batch file: `python validator.py --file samples.txt --visualize`
    * Interactive REPL: `python validator.py --interactive`

---

## 🧪 Verification & Automated Test Results

* **Phase 2 Test Suite:** [`test_phase2.py`](file:///d:/yash/pattern_recognition/grammar_based%20Recognition/test_phase2.py)
* **Execution Command:** `python test_phase2.py`

### Test Execution Output:
```
======================================================================
     GRAMMAR-BASED PATTERN RECOGNITION — PHASE 2 TEST SUITE       
======================================================================

--- 1. Validation Verdict & Error Classification Tests ---
Test 01: [PASS] - Standard valid email -> ACCEPTED
Test 02: [PASS] - Dot in username -> ACCEPTED
Test 03: [PASS] - Plus & underscore in username, hyphen domain -> ACCEPTED
Test 04: [PASS] - Multi-level subdomain -> ACCEPTED
Test 05: [PASS] - Empty string input -> REJECTED (EMPTY_INPUT)
Test 06: [PASS] - Invalid whitespace character -> REJECTED (LEXICAL_ERROR)
Test 07: [PASS] - Invalid symbol # in local -> REJECTED (LEXICAL_ERROR)
Test 08: [PASS] - Missing @ symbol -> REJECTED (STRUCTURAL_ERROR)
Test 09: [PASS] - Double @ symbol -> REJECTED (STRUCTURAL_ERROR)
Test 10: [PASS] - Missing local part -> REJECTED (DERIVATION_SYNTAX_ERROR)
Test 11: [PASS] - Missing domain part -> REJECTED (DERIVATION_SYNTAX_ERROR)
Test 12: [PASS] - Missing TLD / dot -> REJECTED (DERIVATION_SYNTAX_ERROR)
Test 13: [PASS] - Empty domain label -> REJECTED (DERIVATION_SYNTAX_ERROR)
Test 14: [PASS] - Leading separator in local part -> REJECTED (DERIVATION_SYNTAX_ERROR)

--- 2. Parse Tree Visualizer Artifact Verification ---
Test 15: [PASS] - DOT file generated: test_output\test_email_tree.dot
Test 16: [PASS] - Standalone SVG generated: test_output\test_email_tree.svg
Test 17: [PASS] - Unicode ASCII tree generated

--- 3. JSON Serialization & Batch Verification ---
Test 18: [PASS] - Batch processing (3 inputs) succeeded
Test 19: [PASS] - JSON Serialization structured properly

======================================================================
PHASE 2 TEST SUMMARY: 19/19 passed (100.0% accuracy)
======================================================================
```

---

## ⏩ Next Phase Roadmap (Phase 3)

1. **Automated Test Suite & Benchmarks:** Measure execution latency and verify $O(n)$ time complexity.
2. **Grammar Extensibility Demo:** Implement a second pattern class (e.g. `grammar/date.cfg`) to prove zero-code parser extensibility.
3. **Final Project Documentation & Release:** Complete project documentation and polish.
