"""
Expression parser for Teloce templates.

Parses JavaScript expressions used in interpolations and directives.
"""

import re
from typing import List, Optional, Any, Tuple

from teloce.ast.expressions import (
    ExpressionNode, IdentifierNode, LiteralNode, BinaryNode,
    UnaryNode, CallNode, MemberNode, ArrayNode, ObjectNode
)


class ExpressionParser:
    """
    Parses JavaScript expressions.
    """
    
    def __init__(self):
        self.source = ""
        self.position = 0
        self.errors: List[str] = []
    
    def parse(self, source: str) -> Optional[ExpressionNode]:
        """Parse an expression."""
        self.source = source.strip()
        self.position = 0
        self.errors = []
        
        if not self.source:
            return None
        
        return self._parse_expression()
    
    def _parse_expression(self) -> Optional[ExpressionNode]:
        """Parse an expression."""
        return self._parse_assignment()
    
    def _parse_assignment(self) -> Optional[ExpressionNode]:
        """Parse an assignment expression."""
        left = self._parse_logical_or()
        
        if self._match('='):
            right = self._parse_assignment()
            if right:
                # For now, treat as binary expression
                return BinaryNode(left, '=', right)
        
        return left
    
    def _parse_logical_or(self) -> Optional[ExpressionNode]:
        """Parse a logical OR expression."""
        left = self._parse_logical_and()
        
        while self._match('||'):
            right = self._parse_logical_and()
            if right:
                left = BinaryNode(left, '||', right)
        
        return left
    
    def _parse_logical_and(self) -> Optional[ExpressionNode]:
        """Parse a logical AND expression."""
        left = self._parse_equality()
        
        while self._match('&&'):
            right = self._parse_equality()
            if right:
                left = BinaryNode(left, '&&', right)
        
        return left
    
    def _parse_equality(self) -> Optional[ExpressionNode]:
        """Parse an equality expression."""
        left = self._parse_comparison()
        
        while True:
            if self._match('==='):
                right = self._parse_comparison()
                if right:
                    left = BinaryNode(left, '===', right)
            elif self._match('!=='):
                right = self._parse_comparison()
                if right:
                    left = BinaryNode(left, '!==', right)
            elif self._match('=='):
                right = self._parse_comparison()
                if right:
                    left = BinaryNode(left, '==', right)
            elif self._match('!='):
                right = self._parse_comparison()
                if right:
                    left = BinaryNode(left, '!=', right)
            else:
                break
        
        return left
    
    def _parse_comparison(self) -> Optional[ExpressionNode]:
        """Parse a comparison expression."""
        left = self._parse_additive()
        
        while True:
            if self._match('>'):
                right = self._parse_additive()
                if right:
                    left = BinaryNode(left, '>', right)
            elif self._match('>='):
                right = self._parse_additive()
                if right:
                    left = BinaryNode(left, '>=', right)
            elif self._match('<'):
                right = self._parse_additive()
                if right:
                    left = BinaryNode(left, '<', right)
            elif self._match('<='):
                right = self._parse_additive()
                if right:
                    left = BinaryNode(left, '<=', right)
            else:
                break
        
        return left
    
    def _parse_additive(self) -> Optional[ExpressionNode]:
        """Parse an additive expression."""
        left = self._parse_multiplicative()
        
        while True:
            if self._match('+'):
                right = self._parse_multiplicative()
                if right:
                    left = BinaryNode(left, '+', right)
            elif self._match('-'):
                right = self._parse_multiplicative()
                if right:
                    left = BinaryNode(left, '-', right)
            else:
                break
        
        return left
    
    def _parse_multiplicative(self) -> Optional[ExpressionNode]:
        """Parse a multiplicative expression."""
        left = self._parse_unary()
        
        while True:
            if self._match('*'):
                right = self._parse_unary()
                if right:
                    left = BinaryNode(left, '*', right)
            elif self._match('/'):
                right = self._parse_unary()
                if right:
                    left = BinaryNode(left, '/', right)
            elif self._match('%'):
                right = self._parse_unary()
                if right:
                    left = BinaryNode(left, '%', right)
            else:
                break
        
        return left
    
    def _parse_unary(self) -> Optional[ExpressionNode]:
        """Parse a unary expression."""
        if self._match('!'):
            operand = self._parse_unary()
            if operand:
                return UnaryNode('!', operand)
        elif self._match('-'):
            operand = self._parse_unary()
            if operand:
                return UnaryNode('-', operand)
        elif self._match('+'):
            operand = self._parse_unary()
            if operand:
                return UnaryNode('+', operand)
        elif self._match('typeof'):
            operand = self._parse_unary()
            if operand:
                return UnaryNode('typeof', operand)
        
        return self._parse_primary()
    
    def _parse_primary(self) -> Optional[ExpressionNode]:
        """Parse a primary expression."""
        if self._match('('):
            expr = self._parse_expression()
            if self._match(')'):
                return expr
            self.errors.append("Expected ')'")
            return None
        
        if self._match('['):
            return self._parse_array()
        
        if self._match('{'):
            return self._parse_object()
        
        # Literals
        if self._match('true'):
            return LiteralNode(True)
        if self._match('false'):
            return LiteralNode(False)
        if self._match('null'):
            return LiteralNode(None)
        if self._match('undefined'):
            return LiteralNode(None)
        
        # String literal
        if self._match('"'):
            return self._parse_string_literal('"')
        if self._match("'"):
            return self._parse_string_literal("'")
        
        # Number literal
        number = self._match_number()
        if number is not None:
            return LiteralNode(number)
        
        # Identifier
        identifier = self._match_identifier()
        if identifier:
            return self._parse_member_or_call(IdentifierNode(identifier))
        
        return None
    
    def _parse_string_literal(self, quote: str) -> Optional[LiteralNode]:
        """Parse a string literal."""
        start = self.position
        while self.position < len(self.source):
            char = self.source[self.position]
            if char == '\\':
                self.position += 2
                continue
            if char == quote:
                self.position += 1
                value = self.source[start:self.position - 1]
                return LiteralNode(value)
            self.position += 1
        
        self.errors.append("Unterminated string literal")
        return None
    
    def _parse_array(self) -> Optional[ArrayNode]:
        """Parse an array literal."""
        elements = []
        
        while not self._match(']'):
            if self._match(','):
                continue
            element = self._parse_expression()
            if element:
                elements.append(element)
            if self._match(']'):
                break
        
        return ArrayNode(elements)
    
    def _parse_object(self) -> Optional[ObjectNode]:
        """Parse an object literal."""
        properties = []
        
        while not self._match('}'):
            key = self._match_identifier()
            if not key:
                if self._match('"'):
                    key = self._parse_string_literal('"')
                    if key:
                        key = str(key.value)
                elif self._match("'"):
                    key = self._parse_string_literal("'")
                    if key:
                        key = str(key.value)
            
            if not key:
                break
            
            if self._match(':'):
                value = self._parse_expression()
                if value:
                    properties.append((key, value))
            
            self._match(',')
        
        return ObjectNode(properties)
    
    def _parse_member_or_call(self, node: ExpressionNode) -> ExpressionNode:
        """Parse member access or function call."""
        while True:
            if self._match('.'):
                prop = self._match_identifier()
                if prop:
                    node = MemberNode(node, prop)
                else:
                    break
            elif self._match('['):
                index = self._parse_expression()
                if self._match(']') and index:
                    node = MemberNode(node, str(index), computed=True)
                else:
                    break
            elif self._match('('):
                args = []
                while not self._match(')'):
                    if self._match(','):
                        continue
                    arg = self._parse_expression()
                    if arg:
                        args.append(arg)
                    if self._match(')'):
                        break
                node = CallNode(node, args)
            else:
                break
        
        return node
    
    def _match(self, expected: str) -> bool:
        """Match and consume a specific string."""
        if self.position >= len(self.source):
            return False
        
        # Skip whitespace
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1
        
        if self.position >= len(self.source):
            return False
        
        if self.source.startswith(expected, self.position):
            self.position += len(expected)
            return True
        
        return False
    
    def _match_identifier(self) -> Optional[str]:
        """Match an identifier."""
        if self.position >= len(self.source):
            return None
        
        # Skip whitespace
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1
        
        if self.position >= len(self.source):
            return None
        
        start = self.position
        char = self.source[start]
        if char.isalpha() or char == '_' or char == '$':
            self.position += 1
            while self.position < len(self.source):
                char = self.source[self.position]
                if not (char.isalnum() or char == '_' or char == '$'):
                    break
                self.position += 1
            return self.source[start:self.position]
        
        return None
    
    def _match_number(self) -> Optional[float]:
        """Match a number literal."""
        if self.position >= len(self.source):
            return None
        
        # Skip whitespace
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1
        
        if self.position >= len(self.source):
            return None
        
        start = self.position
        has_dot = False
        has_digit = False
        
        while self.position < len(self.source):
            char = self.source[self.position]
            if char.isdigit():
                has_digit = True
                self.position += 1
            elif char == '.' and not has_dot:
                has_dot = True
                self.position += 1
            else:
                break
        
        if has_digit:
            try:
                return float(self.source[start:self.position])
            except ValueError:
                return None
        
        return None
