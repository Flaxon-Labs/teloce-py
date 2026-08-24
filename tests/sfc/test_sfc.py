"""
Tests for the SFC parser.
"""

import pytest

from teloce.sfc.parser import SFCParser
from teloce.sfc.component import Component, ComponentScript, ComponentStyle


class TestSFC:
    """Tests for the SFC parser."""

    def test_parse_basic(self):
        """Test parsing a basic .vel file."""
        source = """
<template>
    <div>Hello</div>
</template>

<script>
export default {
    name: 'Hello'
};
</script>
"""
        parser = SFCParser()
        component = parser.parse(source, 'test.vel')
        
        assert component is not None
        assert component.name == 'Hello'
        assert component.template is not None

    def test_parse_with_style(self):
        """Test parsing with style section."""
        source = """
<template>
    <div class="app">Hello</div>
</template>

<script>
export default {
    name: 'App'
};
</script>

<style scoped>
.app { padding: 20px; }
</style>
"""
        parser = SFCParser()
        component = parser.parse(source, 'test.vel')
        
        assert component is not None
        assert component.name == 'App'
        assert component.style is not None
        assert component.style.css == '.app { padding: 20px; }'
        assert component.style.scoped is True

    def test_parse_missing_template(self):
        """Test parsing with missing template."""
        source = """
<script>
export default {
    name: 'Hello'
};
</script>
"""
        parser = SFCParser()
        component = parser.parse(source, 'test.vel')
        
        assert component is None

    def test_parse_missing_script(self):
        """Test parsing with missing script."""
        source = """
<template>
    <div>Hello</div>
</template>
"""
        parser = SFCParser()
        component = parser.parse(source, 'test.vel')
        
        assert component is not None
        assert component.name == 'test'
        assert component.script is not None

    def test_parse_with_data(self):
        """Test parsing with data function."""
        source = """
<template>
    <div>{{ message }}</div>
</template>

<script>
export default {
    data() {
        return { message: 'Hello' }
    }
};
</script>
"""
        parser = SFCParser()
        component = parser.parse(source, 'test.vel')
        
        assert component is not None
        assert component.script.data is not None
        assert 'message' in component.script.data

    def test_parse_with_methods(self):
        """Test parsing with methods."""
        source = """
<template>
    <button @click="handleClick">Click</button>
</template>

<script>
export default {
    methods: {
        handleClick() {
            console.log('Clicked')
        }
    }
};
</script>
"""
        parser = SFCParser()
        component = parser.parse(source, 'test.vel')
        
        assert component is not None
        assert 'handleClick' in component.script.methods

    def test_parse_with_computed(self):
        """Test parsing with computed."""
        source = """
<template>
    <div>{{ double }}</div>
</template>

<script>
export default {
    data() {
        return { count: 1 }
    },
    computed: {
        double() {
            return this.count * 2
        }
    }
};
</script>
"""
        parser = SFCParser()
        component = parser.parse(source, 'test.vel')
        
        assert component is not None
        assert 'double' in component.script.computed