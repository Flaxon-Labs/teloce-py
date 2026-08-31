"""
Tests for the JavaScript generator.
"""

import pytest
import subprocess
from pathlib import Path
import tempfile

from teloce.javascript.generator import JavaScriptGenerator
from teloce.javascript.dom import DOMGenerator
from teloce.ast.nodes import ElementNode, TextNode, InterpolationNode
from teloce.sfc.parser import SFCParser
from teloce.javascript.helpers import HelperGenerator


class TestJavaScript:
    """Tests for the JavaScript generator."""

    def test_dom_element(self):
        """Test DOM generation for element."""
        dom_gen = DOMGenerator()
        node = ElementNode('div', {'class': 'container'})
        result = dom_gen.generate_element(node)
        
        assert "document.createElement('div')" in result
        assert "setAttribute('class', 'container')" in result

    def test_dom_text(self):
        """Test DOM generation for text."""
        dom_gen = DOMGenerator()
        node = TextNode('Hello World')
        result = dom_gen.generate_text(node)
        
        assert "document.createTextNode('Hello World')" in result

    def test_dom_interpolation(self):
        """Test DOM generation for interpolation."""
        dom_gen = DOMGenerator()
        node = InterpolationNode('message')
        result = dom_gen.generate_interpolation(node)
        
        assert "document.createTextNode(message)" in result

    def test_generator_basic(self):
        source = '<template><h1>{{ title }}</h1></template><script>export default { data() { return { title: "Hello" }; } };</script>'
        component = SFCParser().parse(source, "Basic.vel")
        code = JavaScriptGenerator().generate(component.template, component)

        assert "const Basic" in code
        assert "document.createElement('h1')" in code

    def test_generator_with_component(self):
        source = '<template><button @click="increment">{{ count }}</button></template><script>export default { data() { return { count: 0 }; }, methods: { increment() { this.count++; } } };</script>'
        component = SFCParser().parse(source, "Counter.vel")
        code = JavaScriptGenerator().generate(component.template, component)
        path = Path(__file__).parent / "_generated_legacy_test.js"
        try:
            path.write_text(code, encoding="utf-8")
            checked = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
            assert checked.returncode == 0, checked.stderr
        finally:
            path.unlink(missing_ok=True)

    def test_legacy_generator_preserves_async_methods_lifecycle_and_parameters(self):
        source = '''<template><div>Ready</div></template><script>export default {
          methods: { async load(url, options = {}) { await fetch(url, options); } },
          async mounted() { await this.load("/api"); },
          async errorCaptured(error, instance, info) { await Promise.resolve(error); }
        };</script>'''
        component = SFCParser().parse(source, "AsyncLegacy.vel")
        code = JavaScriptGenerator({"mount": False}).generate(component.template, component)
        assert "async load(url, options = {})" in code
        assert "async mounted()" in code
        assert "async errorCaptured(error, instance, info)" in code

    def test_embedded_signal_helpers_execute_public_api(self):
        source = HelperGenerator().generate_all_helpers() + """
const count = createSignal(1); let seen = 0;
const effect = createEffect(() => { seen = count(); });
count.update(value => value + 1);
if (count.get() !== 2 || seen !== 2) throw new Error('signal helper failed');
effect.stop(); count.set(3);
if (seen !== 2) throw new Error('effect stop failed');
"""
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
            handle.write(source)
            path = Path(handle.name)
        try:
            result = subprocess.run(["node", str(path)], capture_output=True, text=True)
            assert result.returncode == 0, result.stderr
        finally:
            path.unlink(missing_ok=True)
