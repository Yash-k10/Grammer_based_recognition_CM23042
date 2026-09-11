"""
Flask Web Application & API Server for Grammar-Based Pattern Recognition Engine.

Serves the interactive web interface and provides REST APIs for:
- Pattern validation with SVG parse tree generation
- Batch pattern evaluation
- Formal grammar rule inspection (CFG/BNF)
- Live O(n) performance benchmarking
"""

import os
import sys
import json
from flask import Flask, request, jsonify, send_from_directory

# Ensure proper stdout encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from validator import PatternValidator
from benchmark import run_benchmark

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))

# Cache validators
validators = {
    "email": PatternValidator(
        grammar_path=os.path.join(BASE_DIR, "grammar", "email.cfg"),
        output_dir=os.path.join(BASE_DIR, "output")
    ),
    "date": PatternValidator(
        grammar_path=os.path.join(BASE_DIR, "grammar", "date.cfg"),
        output_dir=os.path.join(BASE_DIR, "output")
    )
}


@app.route("/health")
def health():
    """Health check endpoint for cloud hosting services (Render, Railway, etc.)."""
    return jsonify({"status": "healthy", "service": "grammar-pattern-recognition"}), 200


@app.route("/")
def index():
    """Serves the main web application UI."""
    return send_from_directory(os.path.join(BASE_DIR, "static"), "index.html")


@app.route("/api/validate", methods=["POST"])
def api_validate():
    """
    Validates a single input string against the specified grammar.
    """
    data = request.get_json(force=True, silent=True) or {}
    input_str = data.get("input", "").strip()
    grammar_type = data.get("grammar", "email").lower()

    if grammar_type not in validators:
        grammar_type = "email"

    validator = validators[grammar_type]
    res = validator.validate(input_str, generate_visuals=True)

    # Read rendered SVG if available
    svg_content = None
    if res.svg_file and os.path.exists(res.svg_file):
        try:
            with open(res.svg_file, "r", encoding="utf-8") as f:
                svg_content = f.read()
        except Exception:
            pass

    return jsonify({
        "input": res.input_str,
        "is_valid": res.is_valid,
        "verdict": res.verdict,
        "error_code": res.error_code,
        "error_message": res.error_message,
        "matched_components": res.matched_components,
        "tokens": res.tokens,
        "ascii_tree": res.ascii_tree,
        "svg_content": svg_content,
        "grammar": grammar_type
    })


@app.route("/api/batch", methods=["POST"])
def api_batch():
    """
    Validates a batch of inputs and returns aggregated statistics.
    """
    data = request.get_json(force=True, silent=True) or {}
    raw_text = data.get("text", "")
    grammar_type = data.get("grammar", "email").lower()

    if grammar_type not in validators:
        grammar_type = "email"

    lines = [l.strip() for l in raw_text.splitlines() if l.strip() and not l.strip().startswith("#")]
    validator = validators[grammar_type]

    results = []
    accepted_count = 0

    for line in lines:
        res = validator.validate(line, generate_visuals=False)
        if res.is_valid:
            accepted_count += 1
        results.append({
            "input": res.input_str,
            "is_valid": res.is_valid,
            "verdict": res.verdict,
            "error_code": res.error_code,
            "error_message": res.error_message,
            "matched_components": res.matched_components
        })

    total = len(lines)
    rejected_count = total - accepted_count
    rate = (accepted_count / total * 100) if total > 0 else 0.0

    return jsonify({
        "total": total,
        "accepted": accepted_count,
        "rejected": rejected_count,
        "accuracy_rate": round(rate, 1),
        "results": results,
        "grammar": grammar_type
    })


@app.route("/api/grammars", methods=["GET"])
def api_grammars():
    """
    Returns the production rules and non-terminal specifications for loaded grammars.
    """
    def read_file(path):
        full_path = os.path.join(BASE_DIR, path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    return jsonify({
        "email": {
            "title": "Email CFG Grammar",
            "file": "grammar/email.cfg",
            "rules": read_file("grammar/email.cfg"),
            "description": "Validates local identifiers, '@' separator, domain labels, and TLD endings."
        },
        "date": {
            "title": "Calendar Date CFG Grammar",
            "file": "grammar/date.cfg",
            "rules": read_file("grammar/date.cfg"),
            "description": "Validates ISO (YYYY-MM-DD) and European (DD-MM-YYYY) dates with leap-year constraints."
        }
    })


@app.route("/api/samples", methods=["GET"])
def api_samples():
    """
    Returns curated sample presets for both grammars.
    """
    return jsonify({
        "email": {
            "valid": [
                {"label": "Standard Email", "value": "dhanshree01@gmail.com"},
                {"label": "Dot in Username", "value": "john.doe@company.org"},
                {"label": "Subdomain & Country TLD", "value": "admin@sub.domain.co.in"},
                {"label": "Plus Tag & Hyphen", "value": "user+filter@tech-lab.io"}
            ],
            "invalid": [
                {"label": "Missing @", "value": "plainaddress.com", "expected_err": "STRUCTURAL_ERROR"},
                {"label": "Double @", "value": "user@@domain.com", "expected_err": "STRUCTURAL_ERROR"},
                {"label": "Space in Local", "value": "user name@gmail.com", "expected_err": "LEXICAL_ERROR"},
                {"label": "Missing Domain", "value": "user@", "expected_err": "DERIVATION_SYNTAX_ERROR"},
                {"label": "Missing TLD", "value": "user@domain", "expected_err": "DERIVATION_SYNTAX_ERROR"}
            ]
        },
        "date": {
            "valid": [
                {"label": "ISO Dash (YYYY-MM-DD)", "value": "2026-09-10"},
                {"label": "ISO Slash (YYYY/MM/DD)", "value": "2025/12/31"},
                {"label": "ISO Dot (YYYY.MM.DD)", "value": "2024.07.04"},
                {"label": "European Slash (DD/MM/YYYY)", "value": "15/08/1947"},
                {"label": "Leap Year Feb 29 (2024)", "value": "2024-02-29"}
            ],
            "invalid": [
                {"label": "Month > 12", "value": "2026-13-10", "expected_err": "DERIVATION_SYNTAX_ERROR"},
                {"label": "Day > 31", "value": "32/01/2026", "expected_err": "DERIVATION_SYNTAX_ERROR"},
                {"label": "Non-leap Feb 29", "value": "2023-02-29", "expected_err": "DERIVATION_SYNTAX_ERROR"},
                {"label": "Mismatched Sep", "value": "2026-09/10", "expected_err": "DERIVATION_SYNTAX_ERROR"},
                {"label": "Missing Sep", "value": "20260910", "expected_err": "STRUCTURAL_ERROR"}
            ]
        }
    })


@app.route("/api/benchmark", methods=["POST"])
def api_benchmark():
    """
    Executes a performance benchmark across scaling input lengths and returns empirical stats.
    """
    data = request.get_json(force=True, silent=True) or {}
    scales = data.get("scales", [20, 50, 100, 250, 500, 1000, 2500])
    iterations = data.get("iterations", 50)
    grammar = data.get("grammar", "grammar/email.cfg")
    if not os.path.isabs(grammar):
        grammar = os.path.join(BASE_DIR, grammar)

    report = run_benchmark(scales, iterations=iterations, grammar_path=grammar)
    return jsonify(report)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=======================================================")
    print(f"  Grammar-Based Pattern Recognition Web Application")
    print(f"  Server listening at: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
