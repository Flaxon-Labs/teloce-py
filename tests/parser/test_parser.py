"""
Tests for the parser module.
"""

import pytest

from teloce.compiler.parser import Parser
from teloce.compiler.lexer import Lexer, TokenType
from teloce.ast.nodes import ElementNode, TextNode, InterpolationNode, ForNode, IfNode


class TestParser:
    """Tests for the parser."""

    def test_parse_element(self):
        """Test parsing an element."""
        source = "<div>Hello</div>"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast) > 0
        assert isinstance(ast[0], ElementNode)
        assert ast[0].tag == "div"

    def test_parse_text(self):
        """Test parsing text."""
        source = "Hello World"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast) > 0
        assert isinstance(ast[0], TextNode)
        assert ast[0].value == "Hello World"

    def test_parse_interpolation(self):
        """Test parsing interpolation."""
        source = "{{ message }}"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast) > 0
        assert isinstance(ast[0], InterpolationNode)
        assert ast[0].expression == "message"

    def test_parse_nested_elements(self):
        """Test parsing nested elements."""
        source = "<div><span>Hello</span></div>"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast) > 0
        assert isinstance(ast[0], ElementNode)
        assert ast[0].tag == "div"
        assert len(ast[0].children) > 0
        assert isinstance(ast[0].children[0], ElementNode)
        assert ast[0].children[0].tag == "span"

    def test_parse_with_attributes(self):
        """Test parsing elements with attributes."""
        source = '<div class="container" id="main">'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast) > 0
        assert isinstance(ast[0], ElementNode)
        assert ast[0].attributes.get('class') == "container"
        assert ast[0].attributes.get('id') == "main"

    def test_parse_with_event(self):
        """Test parsing elements with events."""
        source = '<button @click="handleClick">Click</button>'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast) > 0
        assert isinstance(ast[0], ElementNode)
        assert len(ast[0].events) > 0
        assert ast[0].events[0].name == "click"
        assert ast[0].events[0].handler == "handleClick"

    def test_parse_with_binding(self):
        """Test parsing elements with bindings."""
        source = '<div :class="className">Content</div>'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast) > 0
        assert isinstance(ast[0], ElementNode)
        assert len(ast[0].bindings) > 0
        assert ast[0].bindings[0].name == "class"
        assert ast[0].bindings[0].value == "className"

    def test_parse_for_named_html_attributes(self):
        source = '<for key="id" item="todo" in="todos"><span>{{ todo.id }}</span></for>'
        ast = Parser(Lexer(source).tokenize()).parse()
        assert ast[0].item == "todo"
        assert ast[0].collection == "todos"
        assert ast[0].key == "id"

    def test_parse_long_form_structural_directives(self):
        source = '<ul><li v-for="(item, index) in items" :key="item.id" v-if="item.visible">{{ index }}:{{ item.name }}</li></ul>'
        parser = Parser(Lexer(source).tokenize())
        ast = parser.parse()

        assert not parser.errors
        loop = ast[0].children[0]
        assert isinstance(loop, ForNode)
        assert loop.item == "item"
        assert loop.collection == "items"
        assert loop.key == "item.id"
        assert isinstance(loop.children[0], IfNode)
        assert loop.children[0].condition == "item.visible"

    def test_parse_long_form_event_and_binding_aliases(self):
        source = '<button v-on:click="save" v-bind:disabled="busy">Save</button>'
        parser = Parser(Lexer(source).tokenize())
        ast = parser.parse()

        assert not parser.errors
        assert ast[0].events[0].name == "click"
        assert ast[0].bindings[0].name == "disabled"

    def test_event_modifiers_are_preserved(self):
        parser = Parser(Lexer('<button @click.prevent.stop="save">Save</button>').tokenize())
        ast = parser.parse()

        assert not parser.errors
        assert ast[0].events[0].name == "click.prevent.stop"

    def test_parse_long_form_visibility_and_content_directives(self):
        source = '<div v-show="visible"><span v-text="label"></span><article v-html="markup"></article></div>'
        parser = Parser(Lexer(source).tokenize())
        ast = parser.parse()

        assert not parser.errors
        assert ast[0].bindings[0].name == "show"
        assert ast[0].children[0].bindings[0].name == "text"
        assert ast[0].children[1].bindings[0].name == "html"
