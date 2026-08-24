"""
Tests for the lexer module.
"""

import pytest

from teloce.compiler.lexer import Lexer, TokenType


class TestLexer:
    """Tests for the lexer."""

    def test_tokenize_text(self):
        """Test tokenizing plain text."""
        source = "Hello World"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert len(tokens) >= 1
        assert tokens[0].type == TokenType.TEXT
        assert tokens[0].value == "Hello World"

    def test_tokenize_tag(self):
        """Test tokenizing an HTML tag."""
        source = "<div>"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.OPEN_TAG
        assert tokens[0].value == "div"

    def test_tokenize_closing_tag(self):
        """Test tokenizing a closing tag."""
        source = "</div>"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.CLOSE_TAG
        assert tokens[0].value == "</div>"

    def test_tokenize_self_closing_tag(self):
        """Test tokenizing a self-closing tag."""
        source = "<img />"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.OPEN_TAG
        assert tokens[0].value == "img"

    def test_tokenize_interpolation(self):
        """Test tokenizing interpolation."""
        source = "{{ message }}"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.INTERPOLATION_START
        assert tokens[1].type == TokenType.INTERPOLATION_EXPR
        assert tokens[1].value == "message"
        assert tokens[2].type == TokenType.INTERPOLATION_END

    def test_tokenize_for(self):
        """Test tokenizing for directive."""
        source = "<for item in items>"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.FOR_START
        assert tokens[0].value == "for"

    def test_tokenize_if(self):
        """Test tokenizing if directive."""
        source = "<if condition=\"isLoggedIn\">"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.IF_START
        assert tokens[0].value == "if"

    def test_tokenize_event(self):
        """Test tokenizing event binding."""
        source = "<button @click=\"handleClick\">"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Find the event token
        event_tokens = [t for t in tokens if t.type == TokenType.EVENT]
        assert len(event_tokens) > 0
        assert event_tokens[0].value == "@click"

    def test_tokenize_binding(self):
        """Test tokenizing binding."""
        source = "<div :class=\"className\">"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Find the binding token
        bind_tokens = [t for t in tokens if t.type == TokenType.BIND]
        assert len(bind_tokens) > 0
        assert bind_tokens[0].value == ":class"

    def test_tokenize_comment(self):
        """Test tokenizing a comment."""
        source = "<!-- comment -->"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.COMMENT
        assert tokens[0].value == " comment "

    def test_tokenize_doctype(self):
        """Test tokenizing a DOCTYPE."""
        source = "<!DOCTYPE html>"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.DOCTYPE