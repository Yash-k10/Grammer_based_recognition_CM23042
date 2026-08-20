# Phase 1 Walkthrough — Core Engine & Grammar Foundation

**Project Title:** Grammar-Based Pattern Recognition Engine  
**Phase Completed:** Phase 1 — Core Engine & Grammar Foundation  
**Date:** August 20, 2026  
**Accuracy Score:** 100% (10/10 Test Cases Passed)  

---

## 🎯 Phase 1 Objectives & Achievements

In Phase 1, we successfully implemented the core formal processing engine for the **Grammar-Based Pattern Recognition Engine**. The system reads raw text input, tokenizes it into terminal symbols, and derives formal parse trees according to Context-Free Grammar (CFG/BNF) production rules.

---

## 🛠️ Key Components Delivered

```
grammar_based Recognition/
├── grammar/
│   └── email.cfg         # Formal CFG / BNF production rules
├── lexer.py              # Tokenizer converting text into terminal symbols
├── parser.py             # LL(1) Recursive-Descent formal parser & tree builder
├── test_phase1.py        # Automated test suite (100% accuracy)
```

---

### 1. Grammar Definition (`grammar/email.cfg`)
* **File:** [`grammar/email.cfg`](file:///d:/yash/pattern_recognition/grammar_based%20Recognition/grammar/email.cfg)
* **Description:** Formally specifies the context-free production rules for email patterns.
* **Production Rules:**
```cfg
EMAIL  -> LOCAL AT DOMAIN DOT TLD
LOCAL  -> WORD | WORD SEP LOCAL
DOMAIN -> WORD | WORD HYPHEN DOMAIN

AT     -> '@'
DOT    -> '.'
HYPHEN -> '-'
SEP    -> '.' | '_' | '-' | '+'
WORD   -> 'WORD' | 'ALPHANUM' | 'LETTERS' | 'DIGITS'
TLD    -> 'com' | 'org' | 'net' | 'edu' | 'gov' | 'io' | 'co' | 'in' | 'info' | 'biz' | 'dev' | 'ai'
```

---

### 2. Lexical Analyzer (`lexer.py`)
* **File:** [`lexer.py`](file:///d:/yash/pattern_recognition/grammar_based%20Recognition/lexer.py)
* **Description:** Scans raw input strings and produces position-aware `Token` objects.
* **Token Types:** `WORD`, `SEP`, `AT`, `HYPHEN`, `DOT`, `TLD`, `INVALID`.
* **Sample Output:**
```python
Input: "dhanshree01@gmail.com"
Tokens:
  - Token(type='WORD', value='dhanshree01', pos=0)
  - Token(type='AT', value='@', pos=11)
  - Token(type='WORD', value='gmail', pos=12)
  - Token(type='DOT', value='.', pos=17)
  - Token(type='TLD', value='com', pos=18)
```

---

### 3. Formal Parser Core (`parser.py`)
* **File:** [`parser.py`](file:///d:/yash/pattern_recognition/grammar_based%20Recognition/parser.py)
* **Description:** Executes recursive-descent LL(1) formal derivations, constructs `ParseTreeNode` hierarchies, extracts sub-pattern components, and produces detailed diagnostic failure messages.
* **Sample Parse Tree (`dhanshree01@gmail.com`):**
```
EMAIL
  LOCAL
    WORD ('dhanshree01')
  AT ('@')
  DOMAIN
    WORD ('gmail')
  DOT ('.')
  TLD ('com')
```
* **Extracted Sub-Patterns:**
  * `local`: `"dhanshree01"`
  * `domain`: `"gmail"`
  * `tld`: `"com"`

---

## 🧪 Verification & Automated Test Results

* **Test Suite File:** [`test_phase1.py`](file:///d:/yash/pattern_recognition/grammar_based%20Recognition/test_phase1.py)
* **Execution Command:** `python test_phase1.py`

### Test Execution Summary:
```
=================================================================
      GRAMMAR-BASED PATTERN RECOGNITION — PHASE 1 TEST SUITE      
=================================================================

Test 01: [PASS] - Standard valid email ('dhanshree01@gmail.com') -> ACCEPTED
Test 02: [PASS] - Dot-separated local part ('john.doe@company.org') -> ACCEPTED
Test 03: [PASS] - Underscore & hyphen domain ('user_123@sub-domain.co.in') -> ACCEPTED
Test 04: [PASS] - Plus separator in local ('test.name+tag@dev.io') -> ACCEPTED
Test 05: [PASS] - Missing '@' separator ('plainaddress') -> REJECTED
Test 06: [PASS] - Missing local part ('@missinglocal.com') -> REJECTED
Test 07: [PASS] - Missing domain name ('user@.com') -> REJECTED
Test 08: [PASS] - Missing TLD ('user@domain') -> REJECTED
Test 09: [PASS] - Multiple '@' symbols ('user@@domain.com') -> REJECTED
Test 10: [PASS] - Invalid space character ('user name@gmail.com') -> REJECTED

=================================================================
SUMMARY: 10/10 tests passed (100.0% accuracy)
=================================================================
```

---

## ⏩ Next Phase Roadmap (Phase 2)

Now that Phase 1 is fully complete and verified:
1. **`validator.py`:** Standalone verdict engine with CLI integration.
2. **`visualize.py`:** Graphviz parse tree image generation (PNG/SVG export).
3. **CLI Pipeline:** Single-command execution tool for pattern validation.
