"""
Validation Engine and CLI Pipeline for Grammar-Based Pattern Recognition.

Combines Lexer, Parser, and Visualizer into a unified validation workflow
with structured verdict categorization, sub-pattern extraction, and interactive CLI capabilities.
"""

import sys
import os
import json
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# Ensure standard output safely encodes UTF-8 across all operating systems and terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from lexer import Lexer, Token
from parser import Parser, ParseTreeNode, ParseResult
from visualize import ParseTreeVisualizer


@dataclass
class ValidationResult:
    """Encapsulates the complete outcome of pattern validation."""
    input_str: str
    is_valid: bool
    verdict: str  # "ACCEPTED" or "REJECTED"
    error_code: Optional[str] = None  # e.g., "LEXICAL_ERROR", "SYNTAX_ERROR"
    error_message: Optional[str] = None
    matched_components: Dict[str, str] = field(default_factory=dict)
    tokens: List[Dict[str, Any]] = field(default_factory=list)
    ascii_tree: Optional[str] = None
    dot_file: Optional[str] = None
    svg_file: Optional[str] = None
    png_file: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts the result to a JSON-serializable dictionary."""
        return {
            "input": self.input_str,
            "is_valid": self.is_valid,
            "verdict": self.verdict,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "matched_components": self.matched_components,
            "tokens": self.tokens,
            "visual_artifacts": {
                "dot": self.dot_file,
                "svg": self.svg_file,
                "png": self.png_file
            }
        }


class PatternValidator:
    """
    Unified validation engine managing the complete recognition pipeline:
    Raw Text -> Lexer -> Parser -> Verdict -> Visualizer
    """

    def __init__(self, grammar_path: str = "grammar/email.cfg", output_dir: str = "output"):
        self.grammar_path = grammar_path
        self.output_dir = output_dir
        self.lexer = Lexer()
        self.parser = Parser(grammar_path=grammar_path)
        self.visualizer = ParseTreeVisualizer(output_dir=output_dir)

    def _classify_error(self, parse_res: ParseResult) -> str:
        """Classifies the root category of validation failure."""
        if not parse_res.error_message:
            return "UNKNOWN_ERROR"
        msg = parse_res.error_message.lower()
        if "empty token stream" in msg or "no input" in msg:
            return "EMPTY_INPUT"
        elif "lexical error" in msg:
            return "LEXICAL_ERROR"
        elif "structural error" in msg or "missing '@'" in msg or "multiple '@'" in msg:
            return "STRUCTURAL_ERROR"
        elif "grammar derivation error" in msg:
            return "DERIVATION_SYNTAX_ERROR"
        return "SYNTAX_ERROR"

    def validate(self, input_str: str, generate_visuals: bool = False, file_prefix: Optional[str] = None) -> ValidationResult:
        """
        Validates a single input string through the complete grammar recognition pipeline.
        
        Args:
            input_str: Raw input string to validate
            generate_visuals: Whether to render DOT/SVG/PNG visual parse tree artifacts
            file_prefix: Optional custom filename prefix for exported visual files
            
        Returns:
            ValidationResult instance with verdict, components, and optional visual paths
        """
        # Step 1: Lexical analysis (Tokenization)
        tokens = self.lexer.tokenize(input_str)
        token_data = [{"type": t.type, "value": t.value, "pos": t.position} for t in tokens]

        # Step 2: Syntactic analysis (LL1 Parsing)
        parse_res = self.parser.parse(tokens)

        # Step 3: Verdict logic & visual rendering
        if parse_res.is_valid:
            ascii_tree = self.visualizer.render_ascii(parse_res.parse_tree) if parse_res.parse_tree else None
            dot_path = None
            svg_path = None
            png_path = None

            if generate_visuals and parse_res.parse_tree:
                safe_name = file_prefix or "".join(c if c.isalnum() else "_" for c in input_str)[:30]
                dot_path = self.visualizer.save_dot(parse_res.parse_tree, f"{safe_name}_tree.dot")
                svg_path = self.visualizer.render_svg(parse_res.parse_tree, f"{safe_name}_tree.svg")
                png_path = self.visualizer.render_graphviz(parse_res.parse_tree, f"{safe_name}_tree", format="png")

            return ValidationResult(
                input_str=input_str,
                is_valid=True,
                verdict="ACCEPTED",
                matched_components=parse_res.matched_components,
                tokens=token_data,
                ascii_tree=ascii_tree,
                dot_file=dot_path,
                svg_file=svg_path,
                png_file=png_path
            )
        else:
            err_code = self._classify_error(parse_res)
            return ValidationResult(
                input_str=input_str,
                is_valid=False,
                verdict="REJECTED",
                error_code=err_code,
                error_message=parse_res.error_message,
                tokens=token_data
            )

    def validate_batch(self, inputs: List[str], generate_visuals: bool = False) -> List[ValidationResult]:
        """Validates a list of input strings."""
        return [self.validate(inp, generate_visuals=generate_visuals) for inp in inputs]


def print_formatted_result(result: ValidationResult, format_type: str = "text"):
    """Prints validation result according to specified presentation format."""
    if format_type == "json":
        print(json.dumps(result.to_dict(), indent=2))
        return

    if format_type == "tree":
        print(f"\nPattern: '{result.input_str}' -> [{result.verdict}]")
        if result.is_valid and result.ascii_tree:
            print(result.ascii_tree)
        elif not result.is_valid:
            print(f"Error ({result.error_code}): {result.error_message}")
        return

    # Default 'text' presentation format
    border = "=" * 65
    print("\n" + border)
    if result.is_valid:
        print(f" VERDICT: [ACCEPTED]  |  Pattern: '{result.input_str}'")
        print(border)
        print(" Matched Sub-Components:")
        for k, v in result.matched_components.items():
            print(f"   * {k:<8}: {v}")
        if result.ascii_tree:
            print("\n Parse Derivation Tree:")
            print(result.ascii_tree)
        if result.svg_file or result.dot_file:
            print(" Exported Visual Artifacts:")
            if result.dot_file:
                print(f"   * DOT Graph: {result.dot_file}")
            if result.svg_file:
                print(f"   * SVG Image: {result.svg_file}")
            if result.png_file:
                print(f"   * PNG Image: {result.png_file}")
    else:
        print(f" VERDICT: [REJECTED]  |  Pattern: '{result.input_str}'")
        print(border)
        print(f" Error Type:    {result.error_code}")
        print(f" Error Message: {result.error_message}")
    print(border)


def run_interactive_mode(validator: PatternValidator, generate_visuals: bool = False, format_type: str = "text"):
    """Starts an interactive REPL session for live pattern evaluation."""
    print("=" * 65)
    print("   Grammar-Based Pattern Recognition Engine — Interactive REPL   ")
    print("   Type any pattern to validate. Type 'exit' or 'quit' to end.  ")
    print("=" * 65)

    while True:
        try:
            user_input = input("\nEnter pattern > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting interactive session.")
                break

            res = validator.validate(user_input, generate_visuals=generate_visuals)
            print_formatted_result(res, format_type=format_type)

        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break


def main():
    parser = argparse.ArgumentParser(
        description="Grammar-Based Pattern Recognition Engine — Validation & Pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validator.py --input "dhanshree01@gmail.com" --visualize
  python validator.py --input "user@@domain.com"
  python validator.py --input "john.doe@company.org" --format json
  python validator.py --file samples.txt --visualize
  python validator.py --interactive --visualize
        """
    )

    parser.add_argument("-i", "--input", type=str, help="Single input pattern string to validate")
    parser.add_argument("-f", "--file", type=str, help="Path to text file with one pattern per line")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive evaluation REPL")
    parser.add_argument("-g", "--grammar", type=str, default="grammar/email.cfg", help="Path to CFG grammar file")
    parser.add_argument("-v", "--visualize", action="store_true", help="Generate parse tree visual files (.dot, .svg, .png)")
    parser.add_argument("--format", choices=["text", "json", "tree"], default="text", help="Output display format")
    parser.add_argument("-o", "--output-dir", type=str, default="output", help="Directory for generated visuals")

    args = parser.parse_args()

    validator = PatternValidator(grammar_path=args.grammar, output_dir=args.output_dir)

    if args.interactive:
        run_interactive_mode(validator, generate_visuals=args.visualize, format_type=args.format)
    elif args.file:
        if not os.path.exists(args.file):
            print(f"Error: Input file '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)

        with open(args.file, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]

        print(f"\nProcessing {len(lines)} patterns from '{args.file}'...")
        results = validator.validate_batch(lines, generate_visuals=args.visualize)
        
        accepted = sum(1 for r in results if r.is_valid)
        rejected = len(results) - accepted

        for r in results:
            print_formatted_result(r, format_type=args.format)

        print(f"\nBATCH SUMMARY: {len(results)} total | {accepted} ACCEPTED | {rejected} REJECTED")
    elif args.input is not None:
        result = validator.validate(args.input, generate_visuals=args.visualize)
        print_formatted_result(result, format_type=args.format)
        sys.exit(0 if result.is_valid else 1)
    else:
        # Default demo if no arguments provided
        demo_sample = "dhanshree01@gmail.com"
        print(f"No arguments provided. Running default demo with '{demo_sample}'...")
        result = validator.validate(demo_sample, generate_visuals=True)
        print_formatted_result(result, format_type="text")
        print("\nTip: Run with --help to see all CLI options.")


if __name__ == "__main__":
    main()
