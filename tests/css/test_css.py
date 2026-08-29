"""
Tests for the CSS module.
"""

import pytest

from teloce.css.parser import CSSParser
from teloce.css.scoped import CSSScoper
from teloce.css.hashing import HashGenerator
from teloce.css.generator import CSSGenerator


class TestCSS:
    """Tests for the CSS module."""

    def test_parser_basic(self):
        """Test basic CSS parsing."""
        source = ".app { padding: 20px; }"
        parser = CSSParser()
        stylesheet = parser.parse(source)
        
        assert len(stylesheet.rules) > 0
        assert stylesheet.rules[0].selector == ".app"
        assert len(stylesheet.rules[0].declarations) > 0
        assert stylesheet.rules[0].declarations[0].property == "padding"
        assert stylesheet.rules[0].declarations[0].value == "20px"

    def test_parser_multiple(self):
        """Test parsing multiple rules."""
        source = """
.app { padding: 20px; }
.header { margin: 10px; }
"""
        parser = CSSParser()
        stylesheet = parser.parse(source)
        
        assert len(stylesheet.rules) == 2

    def test_parser_at_rule(self):
        """Test parsing at-rule."""
        source = "@media (max-width: 600px) { .app { padding: 10px; } }"
        parser = CSSParser()
        stylesheet = parser.parse(source)
        
        assert len(stylesheet.at_rules) > 0
        assert stylesheet.at_rules[0].name == "media"

    def test_scoper_basic(self):
        """Test basic CSS scoping."""
        scoper = CSSScoper()
        source = ".app { padding: 20px; }"
        result = scoper.scope(source, "data-v-abc123")
        
        assert "data-v-abc123" in result
        assert ".app" in result

    def test_hash_generator(self):
        """Test hash generation."""
        hasher = HashGenerator()
        hash_val = hasher.generate("Component")
        
        assert len(hash_val) == 8
        assert hash_val.isalnum()

    def test_hash_generator_scope_id(self):
        """Test scope ID generation."""
        hasher = HashGenerator()
        scope_id = hasher.generate_scope_id("Component")
        
        assert scope_id.startswith("data-v-")
        assert len(scope_id) == 16  # "data-v-" + 8 chars

    def test_generator_basic(self):
        """Test CSS generation."""
        css_gen = CSSGenerator({'scoped': False})
        source = ".app { padding: 20px; }"
        result = css_gen.generate(source, "Component")
        
        assert ".app" in result
        assert "padding: 20px" in result

    def test_scoper_supports_global_deep_and_slotted_selectors(self):
        scoper = CSSScoper()
        result = scoper.scope(
            ":global(.reset) { margin: 0; } .host :deep(.child) { color: red; } :slotted(.item) { color: blue; }",
            "data-v-scope",
        )
        assert ".reset {" in result
        assert ".host[data-v-scope] .child" in result
        assert "[data-v-scope] > .item" in result

    def test_scoper_preserves_nested_selector_commas(self):
        scoper = CSSScoper()
        result = scoper.scope(
            ':is(.card, .panel), [data-label="a,b"] { color: red; }',
            "data-v-scope",
        )
        assert ".card" in result and ".panel" in result
        assert '[data-label="a,b"]' in result

    def test_parser_and_scoper_preserve_declaration_at_rules(self):
        source = '@font-face { font-family: Demo; src: url("demo.woff2"); }'
        stylesheet = CSSParser().parse(source)
        assert stylesheet.at_rules[0].declarations[0].property == 'font-family'
        result = CSSScoper().scope(source, 'data-v-scope')
        assert '@font-face' in result
        assert 'src: url("demo.woff2")' in result

    def test_scoper_preserves_nested_at_rules(self):
        result = CSSScoper().scope(
            '@media (min-width: 600px) { @supports (display: grid) { .card { display: grid; } } }',
            'data-v-scope',
        )
        assert '@media' in result and '@supports' in result
        assert '.card[data-v-scope]' in result

    def test_scoper_does_not_scope_keyframes(self):
        result = CSSScoper().scope(
            '@keyframes pulse { from { opacity: 0; } to { opacity: 1; } }',
            'data-v-scope',
        )
        assert '@keyframes pulse' in result
        assert 'from { opacity: 0' in result
        assert 'from[data-v-scope]' not in result
