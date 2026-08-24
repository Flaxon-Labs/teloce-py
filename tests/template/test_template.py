"""
Tests for the template parser.
"""

import pytest

from teloce.template.lexer import TemplateLexer, TokenType
from teloce.template.parser import TemplateParser
from teloce.ast.nodes import ElementNode, TextNode, InterpolationNode


class TestTemplate:
    """Tests for the template parser."""

    def test_lexer_basic(self):
        """Test basic lexer functionality."""
        source = "<div>Hello</div>"
        lexer = TemplateLexer(source)
        tokens = lexer.tokenize()
        
        assert len(tokens) > 0
        assert tokens[0].type == TokenType.OPEN_TAG
        assert tokens[0].value == "div"

    def test_lexer_interpolation(self):
        """Test lexer with interpolation."""
        source = "{{ message }}"
        lexer = TemplateLexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.INTERPOLATION_START
        assert tokens[1].type == TokenType.INTERPOLATION_EXPR

    def test_parser_basic(self):
        """Test basic parser functionality."""
        source = "<div>Hello</div>"
        lexer = TemplateLexer(source)
        tokens = lexer.tokenize()
        parser = TemplateParser()
        ast = parser.parse(tokens)
        
        assert len(ast) > 0
        assert isinstance(ast[0], ElementNode)
        assert ast[0].tag == "div"

    def test_parser_nested(self):
        """Test parser with nested elements."""
        source = "<div><span>Hello</span></div>"
        lexer = TemplateLexer(source)
        tokens = lexer.tokenize()
        parser = TemplateParser()
        ast = parser.parse(tokens)
        
        assert len(ast) > 0
        assert isinstance(ast[0], ElementNode)
        assert ast[0].tag == "div"
        assert len(ast[0].children) > 0
        assert isinstance(ast[0].children[0], ElementNode)
        assert ast[0].children[0].tag == "span"

    def test_parser_with_interpolation(self):
        """Test parser with interpolation."""
        source = "<div>{{ message }}</div>"
        lexer = TemplateLexer(source)
        tokens = lexer.tokenize()
        parser = TemplateParser()
        ast = parser.parse(tokens)
        
        assert len(ast) > 0
        assert isinstance(ast[0], ElementNode)
        assert len(ast[0].children) > 0
        assert isinstance(ast[0].children[0], InterpolationNode)

    def test_parser_with_attributes(self):
        """Test parser with attributes."""
        source = '<div class="container" id="main">'
        lexer = TemplateLexer(source)
        tokens = lexer.tokenize()
        parser = TemplateParser()
        ast = parser.parse(tokens)
        
        assert len(ast) > 0
        assert isinstance(ast[0], ElementNode)
        assert ast[0].attributes.get('class') == "container"
        assert ast[0].attributes.get('id') == "main"