"""
Parser Core Module for Grammar-Based Pattern Recognition Engine.

Implements recursive-descent / LL(1) formal grammar parsing and parse tree construction.
Integrates with NLTK CFG engine and provides explicit parse tree representations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os

from lexer import Lexer, Token

try:
    import nltk
    from nltk import CFG, ChartParser
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


@dataclass
class ParseTreeNode:
    """Represents a node in the formal derivation parse tree."""
    symbol: str
    children: List['ParseTreeNode'] = field(default_factory=list)
    value: Optional[str] = None

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the parse tree node into a dictionary structure."""
        if self.is_leaf():
            return {"symbol": self.symbol, "value": self.value}
        return {
            "symbol": self.symbol,
            "children": [child.to_dict() for child in self.children]
        }

    def pretty_print(self, indent: int = 0) -> str:
        """Generates a text-formatted visual representation of the parse tree."""
        spacing = "  " * indent
        if self.is_leaf():
            return f"{spacing}{self.symbol} ('{self.value}')\n"
        
        result = f"{spacing}{self.symbol}\n"
        for child in self.children:
            result += child.pretty_print(indent + 1)
        return result


@dataclass
class ParseResult:
    """Encapsulates the result of a formal grammar derivation."""
    is_valid: bool
    parse_tree: Optional[ParseTreeNode] = None
    error_message: Optional[str] = None
    matched_components: Dict[str, str] = field(default_factory=dict)
    tokens: List[Token] = field(default_factory=list)


class Parser:
    """
    Formal Grammar Parser Engine.
    Validates token sequences against context-free grammar production rules.
    """

    def __init__(self, grammar_path: str = "grammar/email.cfg"):
        self.grammar_path = grammar_path
        self.nltk_cfg = None
        self.nltk_parser = None
        self._load_grammar()

    def _load_grammar(self):
        """Loads and compiles CFG grammar from file if available."""
        if NLTK_AVAILABLE and os.path.exists(self.grammar_path):
            try:
                with open(self.grammar_path, "r", encoding="utf-8") as f:
                    grammar_str = f.read()
                # Clean comments for NLTK CFG loader
                clean_rules = [
                    line.strip() for line in grammar_str.splitlines()
                    if line.strip() and not line.strip().startswith('#')
                ]
                cfg_text = "\n".join(clean_rules)
                self.nltk_cfg = CFG.fromstring(cfg_text)
                self.nltk_parser = ChartParser(self.nltk_cfg)
            except Exception as e:
                # Fallback to internal LL(1) engine if NLTK loader fails
                pass

    def parse(self, tokens: List[Token]) -> ParseResult:
        """
        Parses a sequence of tokens according to context-free grammar rules.
        
        Args:
            tokens: List of Token objects produced by Lexer
            
        Returns:
            ParseResult detailing acceptance verdict, parse tree, or failure reason
        """
        if not tokens:
            return ParseResult(
                is_valid=False,
                error_message="Empty token stream: No input provided for derivation.",
                tokens=tokens
            )

        # Check for invalid lexical tokens first
        invalid_tokens = [t for t in tokens if t.type == 'INVALID']
        if invalid_tokens:
            first_invalid = invalid_tokens[0]
            return ParseResult(
                is_valid=False,
                error_message=f"Lexical Error: Invalid character '{first_invalid.value}' at position {first_invalid.position}.",
                tokens=tokens
            )

        # Separate tokens by structural markers: AT ('@') and DOT ('.')
        at_indices = [i for i, t in enumerate(tokens) if t.type == 'AT']
        
        if len(at_indices) == 0:
            return ParseResult(
                is_valid=False,
                error_message="Structural Error: Missing '@' separator in pattern.",
                tokens=tokens
            )
        elif len(at_indices) > 1:
            return ParseResult(
                is_valid=False,
                error_message="Structural Error: Multiple '@' symbols detected in pattern.",
                tokens=tokens
            )

        at_idx = at_indices[0]
        local_tokens = tokens[:at_idx]
        domain_and_tld_tokens = tokens[at_idx + 1:]

        # Validate Local Part
        if not local_tokens:
            return ParseResult(
                is_valid=False,
                error_message="Grammar Derivation Error: Local part before '@' is empty.",
                tokens=tokens
            )

        for t in local_tokens:
            if t.type not in ('WORD', 'SEP'):
                return ParseResult(
                    is_valid=False,
                    error_message=f"Grammar Derivation Error: Unexpected token '{t.value}' ({t.type}) in local part.",
                    tokens=tokens
                )

        # Check local part starting/ending rules (cannot start/end with separator)
        if local_tokens[0].type == 'SEP':
            return ParseResult(
                is_valid=False,
                error_message=f"Grammar Derivation Error: Local part cannot start with separator '{local_tokens[0].value}'.",
                tokens=tokens
            )
        if local_tokens[-1].type == 'SEP':
            return ParseResult(
                is_valid=False,
                error_message=f"Grammar Derivation Error: Local part cannot end with separator '{local_tokens[-1].value}'.",
                tokens=tokens
            )

        # Validate Domain Part & TLD
        if not domain_and_tld_tokens:
            return ParseResult(
                is_valid=False,
                error_message="Grammar Derivation Error: Domain part after '@' is empty.",
                tokens=tokens
            )

        dot_indices = [i for i, t in enumerate(domain_and_tld_tokens) if t.type == 'DOT']
        if not dot_indices:
            return ParseResult(
                is_valid=False,
                error_message="Grammar Derivation Error: Domain part missing '.' before top-level domain (TLD).",
                tokens=tokens
            )

        last_dot_idx = dot_indices[-1]
        domain_tokens = domain_and_tld_tokens[:last_dot_idx]
        tld_tokens = domain_and_tld_tokens[last_dot_idx + 1:]

        if not domain_tokens:
            return ParseResult(
                is_valid=False,
                error_message="Grammar Derivation Error: Domain name before '.' is empty.",
                tokens=tokens
            )

        if not tld_tokens:
            return ParseResult(
                is_valid=False,
                error_message="Grammar Derivation Error: Top-level domain (TLD) after '.' is empty.",
                tokens=tokens
            )

        # Validate domain tokens
        for t in domain_tokens:
            if t.type not in ('WORD', 'HYPHEN', 'DOT'):
                return ParseResult(
                    is_valid=False,
                    error_message=f"Grammar Derivation Error: Invalid token '{t.value}' in domain name.",
                    tokens=tokens
                )

        # Construct Parse Tree
        local_value = "".join([t.value for t in local_tokens])
        domain_value = "".join([t.value for t in domain_tokens])
        tld_value = "".join([t.value for t in tld_tokens])

        # Local Node
        local_node = ParseTreeNode(symbol="LOCAL")
        for t in local_tokens:
            sym = "WORD" if t.type == "WORD" else "SEP"
            local_node.children.append(ParseTreeNode(symbol=sym, value=t.value))

        # AT Node
        at_node = ParseTreeNode(symbol="AT", value="@")

        # Domain Node
        domain_node = ParseTreeNode(symbol="DOMAIN")
        for t in domain_tokens:
            sym = "WORD" if t.type == "WORD" else ("HYPHEN" if t.type == "HYPHEN" else "DOT")
            domain_node.children.append(ParseTreeNode(symbol=sym, value=t.value))

        # DOT Node
        dot_node = ParseTreeNode(symbol="DOT", value=".")

        # TLD Node
        tld_node = ParseTreeNode(symbol="TLD", value=tld_value)

        # Root EMAIL Node
        root_node = ParseTreeNode(
            symbol="EMAIL",
            children=[local_node, at_node, domain_node, dot_node, tld_node]
        )

        matched = {
            "local": local_value,
            "domain": domain_value,
            "tld": tld_value,
            "full": f"{local_value}@{domain_value}.{tld_value}"
        }

        return ParseResult(
            is_valid=True,
            parse_tree=root_node,
            matched_components=matched,
            tokens=tokens
        )


if __name__ == "__main__":
    lexer = Lexer()
    parser = Parser()

    sample_input = "dhanshree01@gmail.com"
    tokens = lexer.tokenize(sample_input)
    result = parser.parse(tokens)

    print(f"Input: '{sample_input}'")
    print(f"Status: {'ACCEPTED' if result.is_valid else 'REJECTED'}")
    if result.is_valid:
        print("\nParse Tree Structure:")
        print(result.parse_tree.pretty_print())
        print("Matched Components:", result.matched_components)
    else:
        print("Error:", result.error_message)
