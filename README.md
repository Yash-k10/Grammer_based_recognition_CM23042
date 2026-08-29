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
├── grammar/          # CFG/BNF production rules per pattern class
│   └── email.cfg
├── lexer.py          # Tokenizes raw input into terminal symbols
├── parser.py         # Recursive-descent / LL(1) parser
├── validator.py       # Accept/reject logic based on derivation success
├── visualize.py       # Renders parse trees via Graphviz
├── tests/             # Valid/invalid sample sets + unit tests
└── README.md
```

## Getting Started

```bash
git clone https://github.com/Dhanshree010/Pattern-Vector-System.git
cd Pattern-Vector-System
pip install -r requirements.txt
```

### Usage

**1. Validate a single pattern with visual tree export:**
```bash
python validator.py --input "dhanshree01@gmail.com" --visualize
```

**2. Output structured JSON:**
```bash
python validator.py --input "dhanshree01@gmail.com" --format json
```

**3. Batch validate a dataset file:**
```bash
python validator.py --file samples.txt --visualize
```

**4. Interactive REPL Mode:**
```bash
python validator.py --interactive --visualize
```

**5. Run Phase 1 and Phase 2 Automated Test Suites:**
```bash
python test_phase1.py
python test_phase2.py
```

Output includes the accept/reject verdict, error classifications, matched components, terminal Unicode parse tree, and exported visual tree diagrams (`.svg`, `.dot`, `.png`).

## Results

- **100%** classification accuracy across valid & invalid edge cases (19/19 tests in Phase 2)
- **Structured Rejection Diagnoses**: Categorized error reporting (`EMPTY_INPUT`, `LEXICAL_ERROR`, `STRUCTURAL_ERROR`, `DERIVATION_SYNTAX_ERROR`)
- **Multi-Format Tree Visualization**: Generates Graphviz DOT, pure-Python SVG diagrams, and Unicode terminal trees
- **O(n)** linear parse time using an unambiguous LL(1) grammar

## Extending to New Pattern Classes

Add a new grammar file under `grammar/` (e.g. `grammar/date.cfg`) following the same CFG/BNF format — the tokenizer and parser are grammar-driven and don't need to change.

## Roadmap

- [ ] Additional grammars: dates, simple code syntax
- [ ] Context-sensitive grammar support
- [ ] Web-based demo for interactive parse tree viewing

## Author

**Dhanshree** — AI/ML Engineering, Sipna College of Engineering & Technology (SBJIT), Amravati

## License

MIT
