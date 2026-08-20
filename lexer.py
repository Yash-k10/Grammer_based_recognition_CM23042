"""
Lexer (Tokenizer) Module for Grammar-Based Pattern Recognition Engine.

Converts raw input strings into terminal tokens recognized by context-free grammars (CFG).
"""

from dataclasses import dataclass
from typing import List
import re


@dataclass
class Token:
    """Represents a single terminal token generated from raw input."""
    type: str
    value: str
    position: int

    def __repr__(self) -> str:
        return f"Token(type='{self.type}', value='{self.value}', pos={self.position})"


class Lexer:
    """
    Lexical analyzer for tokenizing input text into terminal symbols.
    Supports email pattern tokenization and generic grammar terminal matching.
    """

    KNOWN_TLDS = {
        'com', 'org', 'net', 'edu', 'gov', 'io', 'co', 'in', 'info',
        'biz', 'dev', 'ai', 'uk', 'ca', 'de', 'jp', 'fr', 'us'
    }

    def __init__(self):
        pass

    def tokenize(self, input_str: str) -> List[Token]:
        """
        Tokenizes an input string into a list of Token objects.
        
        Args:
            input_str: Raw input string (e.g. "dhanshree01@gmail.com")
            
        Returns:
            List of Token instances
        """
        if not input_str or not isinstance(input_str, str):
            return []

        tokens: List[Token] = []
        at_count = input_str.count('@')

        if at_count == 1:
            local_part, domain_full = input_str.split('@', 1)
            
            # 1. Tokenize local part
            curr = 0
            while curr < len(local_part):
                char = local_part[curr]
                if char.isalnum():
                    match = re.match(r'^[a-zA-Z0-9]+', local_part[curr:])
                    val = match.group(0)
                    tokens.append(Token(type='WORD', value=val, position=curr))
                    curr += len(val)
                elif char in '._-+':
                    tokens.append(Token(type='SEP', value=char, position=curr))
                    curr += 1
                else:
                    tokens.append(Token(type='INVALID', value=char, position=curr))
                    curr += 1

            # 2. Add AT token
            at_pos = len(local_part)
            tokens.append(Token(type='AT', value='@', position=at_pos))

            # 3. Tokenize domain part
            if '.' in domain_full:
                last_dot_idx = domain_full.rfind('.')
                domain_name = domain_full[:last_dot_idx]
                tld_part = domain_full[last_dot_idx + 1:]

                curr = at_pos + 1
                sub_curr = 0
                while sub_curr < len(domain_name):
                    char = domain_name[sub_curr]
                    if char.isalnum():
                        match = re.match(r'^[a-zA-Z0-9]+', domain_name[sub_curr:])
                        val = match.group(0)
                        tokens.append(Token(type='WORD', value=val, position=curr + sub_curr))
                        sub_curr += len(val)
                    elif char == '-':
                        tokens.append(Token(type='HYPHEN', value='-', position=curr + sub_curr))
                        sub_curr += 1
                    elif char == '.':
                        tokens.append(Token(type='DOT', value='.', position=curr + sub_curr))
                        sub_curr += 1
                    else:
                        tokens.append(Token(type='INVALID', value=char, position=curr + sub_curr))
                        sub_curr += 1

                dot_pos = at_pos + 1 + len(domain_name)
                tokens.append(Token(type='DOT', value='.', position=dot_pos))

                tld_pos = dot_pos + 1
                tld_type = 'TLD' if tld_part.lower() in self.KNOWN_TLDS or tld_part.isalpha() else 'WORD'
                tokens.append(Token(type=tld_type, value=tld_part, position=tld_pos))

            else:
                curr = at_pos + 1
                tokens.append(Token(type='WORD', value=domain_full, position=curr))

        else:
            curr = 0
            length = len(input_str)
            while curr < length:
                char = input_str[curr]
                if char.isalnum():
                    match = re.match(r'^[a-zA-Z0-9]+', input_str[curr:])
                    val = match.group(0)
                    t_type = 'TLD' if val.lower() in self.KNOWN_TLDS else 'WORD'
                    tokens.append(Token(type=t_type, value=val, position=curr))
                    curr += len(val)
                elif char == '@':
                    tokens.append(Token(type='AT', value='@', position=curr))
                    curr += 1
                elif char == '.':
                    tokens.append(Token(type='DOT', value='.', position=curr))
                    curr += 1
                elif char == '-':
                    tokens.append(Token(type='HYPHEN', value='-', position=curr))
                    curr += 1
                elif char in '_+':
                    tokens.append(Token(type='SEP', value=char, position=curr))
                    curr += 1
                else:
                    tokens.append(Token(type='INVALID', value=char, position=curr))
                    curr += 1

        return tokens


if __name__ == "__main__":
    lexer = Lexer()
    sample = "dhanshree01@gmail.com"
    toks = lexer.tokenize(sample)
    print(f"Tokens for '{sample}':")
    for t in toks:
        print(" ", t)
