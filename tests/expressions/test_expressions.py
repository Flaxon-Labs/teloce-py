"""
Tests for the expressions module.
"""

import pytest

from teloce.expressions.lexer import ExpressionLexer, TokenType
from teloce.expressions.parser import ExpressionParser
from teloce.expressions.ast import (
    IdentifierNode, LiteralNode, BinaryNode, UnaryNode,
    CallNode, MemberNode, ArrayNode, ObjectNode, AssignmentNode
)


class TestExpressions:
    """Tests for expressions."""

    def test_lexer_identifier(self):
        """Test lexer with identifier."""
        source = "message"
        lexer = ExpressionLexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "message"

    def test_lexer_literal(self):
        """Test lexer with literals."""
        source = "123"
        lexer = ExpressionLexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "123"

    def test_lexer_string(self):
        """Test lexer with strings."""
        source = '"hello"'
        lexer = ExpressionLexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"

    def test_lexer_operator(self):
        """Test lexer with operators."""
        source = "a + b"
        lexer = ExpressionLexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "a"
        assert tokens[1].type == TokenType.PLUS
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[2].value == "b"

    def test_parser_identifier(self):
        """Test parser with identifier."""
        source = "message"
        lexer = ExpressionLexer(source)
        tokens = lexer.tokenize()
        parser = ExpressionParser()
        node = parser.parse(tokens)
        
        assert isinstance(node, IdentifierNode)
        assert node.name == "message"

    def test_parser_literal(self):
        """Test parser with literals."""
        source = "123"
        lexer = ExpressionLexer(source)
        tokens = lexer.tokenize()
        parser = ExpressionParser()
        node = parser.parse(tokens)
        
        assert isinstance(node, LiteralNode)
        assert node.value == 123

    def test_parser_string(self):
        """Test parser with strings."""
        source = '"hello"'
        lexer = ExpressionLexer(source)
        tokens = lexer.tokenize()
        parser = ExpressionParser()
        node = parser.parse(tokens)
        
        assert isinstance(node, LiteralNode)
        assert node.value == "hello"

    def test_parser_binary(self):
        """Test parser with binary expression."""
        source = "a + b"
        lexer = ExpressionLexer(source)
        tokens = lexer.tokenize()
        parser = ExpressionParser()
        node = parser.parse(tokens)
        
        assert isinstance(node, BinaryNode)
        assert node.operator == "+"

    def test_parser_call(self):
        """Test parser with function call."""
        source = "foo()"
        lexer = ExpressionLexer(source)
        tokens = lexer.tokenize()
        parser = ExpressionParser()
        node = parser.parse(tokens)
        
        assert isinstance(node, CallNode)
        assert isinstance(node.callee, IdentifierNode)
        assert node.callee.name == "foo"

    def test_parser_member(self):
        """Test parser with member access."""
        source = "user.name"
        lexer = ExpressionLexer(source)
        tokens = lexer.tokenize()
        parser = ExpressionParser()
        node = parser.parse(tokens)
        
        assert isinstance(node, MemberNode)
        assert isinstance(node.object, IdentifierNode)
        assert node.object.name == "user"
        assert node.property == "name"

    def test_parser_array(self):
        """Test parser with array literal."""
        source = "[1, 2, 3]"
        lexer = ExpressionLexer(source)
        tokens = lexer.tokenize()
        parser = ExpressionParser()
        node = parser.parse(tokens)
        
        assert isinstance(node, ArrayNode)
        assert len(node.elements) == 3

    def test_compound_assignment_round_trips(self):
        source = "count += step"
        lexer = ExpressionLexer(source)
        parser = ExpressionParser()
        node = parser.parse(lexer.tokenize())

        assert not parser.errors
        assert isinstance(node, AssignmentNode)
        assert node.operator == "+="

    def test_exponentiation_is_right_associative(self):
        parser = ExpressionParser()
        node = parser.parse(ExpressionLexer("2 ** 3 ** 2").tokenize())

        assert not parser.errors
        assert isinstance(node, BinaryNode)
        assert node.operator == "**"
        assert isinstance(node.right, BinaryNode)
        assert node.right.operator == "**"
