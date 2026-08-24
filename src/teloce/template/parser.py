"""Canonical template parser facade."""

from typing import List, Any
import json

from teloce.compiler.lexer import Lexer
from teloce.compiler.parser import Parser
from teloce.ast.nodes import ASTNode


class TemplateParser:
    """Parse template source into the canonical Teloce AST."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def parse(self, source: Any, filename: str = "<input>") -> List[ASTNode]:
        self.errors = []
        self.warnings = []
        # Keep compatibility with the original public API, which accepted
        # tokens from TemplateLexer, while using the canonical parser.
        if isinstance(source, list):
            source = self._tokens_to_source(source)
        if not source or not source.strip():
            self.warnings.append(f"Empty template in {filename}")
            return []

        lexer = Lexer(source)
        tokens = lexer.tokenize()
        self.errors.extend(lexer.errors)
        if self.errors:
            return []

        parser = Parser(tokens)
        ast = parser.parse()
        self.errors.extend(parser.errors)
        return [] if self.errors else ast

    def _tokens_to_source(self, tokens: list) -> str:
        """Reconstruct lossless-enough template text from legacy tokens."""
        from teloce.template.lexer import TokenType
        out = []
        open_tags = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            kind = token.type
            if kind == TokenType.EOF:
                break
            if kind == TokenType.OPEN_TAG:
                out.append(f"<{token.value}")
                tag_name = token.value
                i += 1
                while i < len(tokens) and tokens[i].type not in {
                    TokenType.OPEN_TAG, TokenType.CLOSE_TAG, TokenType.TEXT,
                    TokenType.INTERPOLATION_START, TokenType.EOF,
                }:
                    current = tokens[i]
                    if current.type == TokenType.ATTRIBUTE_NAME:
                        out.append(" " + current.value)
                        if i + 1 < len(tokens) and tokens[i + 1].type == TokenType.ATTRIBUTE_VALUE:
                            out.append("=" + json.dumps(tokens[i + 1].value))
                            i += 1
                    elif current.type == TokenType.EVENT:
                        out.append(" " + current.value)
                        if i + 1 < len(tokens) and tokens[i + 1].type == TokenType.ATTRIBUTE_VALUE:
                            out.append("=" + json.dumps(tokens[i + 1].value))
                            i += 1
                    elif current.type == TokenType.BIND:
                        out.append(" " + current.value)
                        if i + 1 < len(tokens) and tokens[i + 1].type == TokenType.ATTRIBUTE_VALUE:
                            out.append("=" + json.dumps(tokens[i + 1].value))
                            i += 1
                    elif current.type == TokenType.SELF_CLOSE_TAG:
                        out.append("/")
                    i += 1
                out.append(">")
                if not any(t.type == TokenType.SELF_CLOSE_TAG for t in tokens[max(0, i - 1):i]):
                    open_tags.append(tag_name)
                continue
            if kind in {TokenType.CLOSE_TAG, TokenType.FOR_END, TokenType.IF_END}:
                out.append(token.value)
                if kind == TokenType.CLOSE_TAG and open_tags:
                    open_tags.pop()
            elif kind == TokenType.TEXT:
                out.append(token.value)
            elif kind == TokenType.INTERPOLATION_START:
                out.append("{{")
                if i + 1 < len(tokens) and tokens[i + 1].type == TokenType.INTERPOLATION_EXPR:
                    out.append(tokens[i + 1].value)
                    i += 1
                out.append("}}")
            i += 1
        while open_tags:
            out.append(f"</{open_tags.pop()}>")
        return ''.join(out)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)
