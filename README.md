# Grammar-Based Pattern Recognition

A parser that identifies patterns in real-world input by testing it against formal grammar rules — accepting what fits the structure, and extracting what matches.

## Why

Real patterns — emails, dates, code syntax, sentences — aren't random strings; they follow structural rules. Plain keyword or regex matching breaks the moment structure gets nested, variable, or context-dependent. This project defines formal grammar rules (CFG/BNF) so a parser can systematically **accept**, **reject**, and **extract** patterns, instead of guessing.

## How It Works

```
Define Grammar → Tokenize Input → Parse & Derive → Match / Reject → Output Parse Tree
```

1. **Define Grammar** — formal CFG/BNF production rules for the target pattern class
2. **Tokenize Input** — raw text split into terminal symbols the grammar understands
3. **Parse & Derive** — the parser attempts a derivation using the grammar rules
4. **Match / Reject** — input is accepted if a valid derivation exists, else rejected
5. **Output Parse Tree** — the matched structure is returned, with sub-patterns extracted

Grammar rules are recursive by nature, so the parser naturally handles nested and variable-length patterns — something flat regex matching can't fully capture.

## Example

```
Input:  "dhanshree01@gmail.com"
Result: ACCEPTED

        EMAIL
       /  |   \
    NAME  @   DOMAIN.TLD
   /   \        /    \
letters digits domain  tld
```

An invalid pattern simply has no derivation — no tree, no match.

## Tech Stack

| Tool | Role |
|---|---|
| Python | Core language |
| PLY / ANTLR | Parser generator |
| Regex module | Lexer / tokenizer |
| NLTK (CFG) | Grammar-based parsing |
| Graphviz | Parse tree visualization |

## Project Structure

```
.
├── grammar/                  # Formal CFG/BNF production rules
│   ├── email.cfg             # Email pattern grammar
│   └── date.cfg              # Calendar date pattern grammar (ISO & European)
├── tests/                    # Automated QA test suite
│   ├── test_lexer.py         # Unit tests for tokenization
│   ├── test_parser.py        # Unit tests for CFG derivations
│   ├── test_validator.py     # Unit tests for verdicts & visual outputs
│   ├── test_extensibility.py # Unit tests for date grammar extensibility
│   ├── test_benchmark.py     # Unit tests for benchmark suite
│   └── run_all_tests.py      # Master test discovery & execution runner
├── lexer.py                  # Tokenizes raw input into terminal symbols
├── parser.py                 # Recursive-descent / LL(1) parser
├── validator.py              # Accept/reject logic and unified CLI pipeline
├── visualize.py              # Renders parse trees to SVG, DOT, and Unicode ASCII
├── benchmark.py              # Performance benchmark & O(n) complexity evaluator
├── requirements.txt          # Python dependencies
├── test_phase1.py            # Phase 1 test suite (10/10 passed)
├── test_phase2.py            # Phase 2 test suite (19/19 passed)
├── test_phase3.py            # Phase 3 QA test suite (26/26 passed)
├── PROJECT_PLAN.md           # 3-Phase roadmap and deliverables matrix
└── README.md
```

## Getting Started

```bash
git clone https://github.com/Yash-k10/Grammer_based_recognition_CM23042.git
cd Grammer_based_recognition_CM23042
pip install -r requirements.txt
```

### Usage

**1. Validate an email pattern with visual tree export:**
```bash
python validator.py --input "dhanshree01@gmail.com" --visualize
```

**2. Validate a calendar date pattern using secondary grammar:**
```bash
python validator.py --grammar grammar/date.cfg --input "2026-09-10" --visualize
python validator.py --grammar grammar/date.cfg --input "15/08/1947" --format json
```

**3. Output structured JSON:**
```bash
python validator.py --input "dhanshree01@gmail.com" --format json
```

**4. Batch validate a dataset file:**
```bash
python validator.py --file samples.txt --visualize
```

**5. Interactive REPL Mode:**
```bash
python validator.py --interactive --visualize
```

**6. Run Performance Benchmark ($O(n)$ Linear Complexity):**
```bash
python benchmark.py --scales "10,25,50,100,250,500,1000,2500,5000" --iterations 100
```
Generates structured data at `output/benchmark_report.json` and visual curve at `output/benchmark_complexity.svg`.

**7. Run Automated Test Suites:**
```bash
# Run complete discovered test suite (39 tests)
python tests/run_all_tests.py

# Run Phase 3 QA verification suite (26 tests)
python test_phase3.py
```

Output includes the accept/reject verdict, error classifications, matched components, terminal Unicode parse tree, and exported visual tree diagrams (`.svg`, `.dot`, `.png`).

## Results & Benchmarks

- **100% Classification Accuracy**: Across all hand-labeled valid & invalid edge cases (39/39 tests in `tests/`, 26/26 in Phase 3 QA).
- **Structured Diagnostics**: Rejections categorized into `EMPTY_INPUT`, `LEXICAL_ERROR`, `STRUCTURAL_ERROR`, and `DERIVATION_SYNTAX_ERROR`.
- **Multi-Format Tree Visualization**: Generates Graphviz DOT, pure-Python SVG diagrams, and Unicode terminal trees.
- **Empirically Verified $O(n)$ Linear Parsing**:
  - Regression Fit: **$R^2 = 0.9907$** (Pearson $r = 0.9953$).
  - Processing Slope: **$0.3243\,\mu s$ per character**.
  - Scales effortlessly from 20 chars ($13.6\,\mu s$) to 5,000 chars ($1.67\,\text{ms}$).
- **Zero-Code Grammar Extensibility**: Added calendar date grammar (`date.cfg`) supporting ISO (`YYYY-MM-DD`, `YYYY/MM/DD`, `YYYY.MM.DD`) and European (`DD-MM-YYYY`, `DD/MM/YYYY`) formats with leap-year semantic validation.

## Roadmap & Milestones

- [x] **Phase 1**: Core Engine & Grammar Foundation (`email.cfg`, `lexer.py`, `parser.py`) — **100%**
- [x] **Phase 2**: Validation Engine, Visualization & CLI Pipeline (`validator.py`, `visualize.py`) — **100%**
- [x] **Phase 3**: Quality Assurance, Benchmarking & Documentation (`tests/`, `date.cfg`, `benchmark.py`) — **100%**

## Author

**Dhanshree** — AI/ML Engineering, Sipna College of Engineering & Technology (SBJIT), Amravati

## License

MIT
