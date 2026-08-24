"""
Integration tests for Teloce.
"""

import pytest
from pathlib import Path
import tempfile

from teloce.compiler.compiler import compile
from teloce.sfc.parser import SFCParser
from teloce.build.builder import Builder
from teloce.build import build_project
from teloce.project.scanner import ProjectScanner


class TestIntegration:
    """Integration tests for Teloce."""

    def test_full_compile_flow(self):
        """Test the full compilation flow."""
        source = """
<template>
    <div>
        <h1>{{ title }}</h1>
        <p>Count: {{ count }}</p>
        <button @click="increment">+</button>
    </div>
</template>

<script>
export default {
    data() {
        return {
            title: 'Hello Teloce',
            count: 0
        };
    },
    methods: {
        increment() {
            this.count++;
        }
    }
};
</script>

<style scoped>
h1 { color: blue; }
button { background: #6366f1; color: white; }
</style>
"""
        result = compile(source)
        
        assert result['success'] is True
        assert 'code' in result
        assert 'css' in result
        assert 'data' in result['code']
        assert 'increment' in result['code']

    def test_sfc_to_component(self):
        """Test SFC parsing to component."""
        source = """
<template>
    <div>Hello</div>
</template>

<script>
export default {
    name: 'Hello'
};
</script>

<style scoped>
.hello { color: blue; }
</style>
"""
        parser = SFCParser()
        component = parser.parse(source, 'Hello.vel')
        
        assert component is not None
        assert component.name == 'Hello'
        assert component.template is not None
        assert component.style.css == '.hello { color: blue; }'

    def test_builder_flow(self):
        """Test builder flow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a .vel file
            vel_path = Path(tmpdir) / 'static' / 'js' / 'App.vel'
            vel_path.parent.mkdir(parents=True)
            vel_path.write_text("""
<template>
    <div>Hello</div>
</template>

<script>
export default {
    name: 'App'
};
</script>
""")
            
            builder = Builder({'dev': True})
            result = builder.build(tmpdir)
            
            assert result['total'] >= 1
            assert result['compiled'] >= 1
            assert result['duration'] > 0

    def test_server_startup_build_helper(self):
        """The Python host can compile components before starting its server."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vel_path = Path(tmpdir) / 'static' / 'js' / 'App.vel'
            vel_path.parent.mkdir(parents=True)
            vel_path.write_text('<template><div>Ready</div></template>')
            result = build_project(tmpdir, options={'dev': True})
            assert result['failed'] == 0
            assert (Path(tmpdir) / 'dist' / 'static' / 'js' / 'App.js').exists()

    def test_scanner_flow(self):
        """Test scanner flow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .vel files
            vel_path = Path(tmpdir) / 'static' / 'js' / 'App.vel'
            vel_path.parent.mkdir(parents=True)
            vel_path.write_text("""
<template><div>App</div></template>
<script>export default { name: 'App' }</script>
""")
            
            vel_path2 = Path(tmpdir) / 'static' / 'js' / 'components' / 'Card.vel'
            vel_path2.parent.mkdir(parents=True)
            vel_path2.write_text("""
<template><div>Card</div></template>
<script>export default { name: 'Card' }</script>
""")
            
            scanner = ProjectScanner()
            files = scanner.scan(tmpdir)
            
            assert len(files) == 2
            assert any('App.vel' in str(f) for f in files)
            assert any('Card.vel' in str(f) for f in files)
