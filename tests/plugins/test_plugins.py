"""
Tests for the plugins module.
"""

import pytest

from teloce.plugins.api import Plugin, PluginAPI
from teloce.plugins.registry import PluginRegistry
from teloce.plugins.directives import DirectivePlugin
from teloce.plugins.filters import FilterPlugin
from teloce.plugins.hooks import HookPlugin, HookManager
from teloce.compiler.compiler import compile


class TestPlugins:
    """Tests for the plugins module."""

    def test_plugin_basic(self):
        """Test basic plugin."""
        class MyPlugin(Plugin):
            def install(self, api):
                api.register_filter('test', lambda x: x)
        
        plugin = MyPlugin(name='test-plugin', version='1.0.0')
        assert plugin.name == 'test-plugin'
        assert plugin.version == '1.0.0'

    def test_plugin_api(self):
        """Test plugin API."""
        registry = PluginRegistry()
        api = PluginAPI(registry)
        
        # Register a filter
        api.register_filter('test', lambda x: x)
        assert api.get_filter('test') is not None
        
        # Register a directive
        api.register_directive('test', {})
        assert api.get_directive('test') is not None

    def test_plugin_api_accepts_npm_style_descriptors(self):
        registry = PluginRegistry()
        api = PluginAPI(registry)
        api.register_filter({"name": "reverse", "transform": lambda value: value[::-1]})
        api.register_directive({"name": "focus", "render": lambda element: element.focus()})
        api.register_component({"name": "Card", "component": {"render": lambda: "card"}})
        assert api.get_filter("reverse")("abc") == "cba"
        assert api.get_directive("focus")["name"] == "focus"
        assert api.get_component("Card")["render"]() == "card"

    def test_plugin_registry(self):
        """Test plugin registry."""
        registry = PluginRegistry()
        api = PluginAPI(registry)
        registry.set_api(api)
        
        class MyPlugin(Plugin):
            def install(self, api):
                api.register_filter('test', lambda x: x)
        
        plugin = MyPlugin(name='test-plugin', version='1.0.0')
        registry.register(plugin)
        
        assert registry.has('test-plugin')
        assert len(registry.get_all()) == 1

    def test_directive_plugin(self):
        """Test directive plugin."""
        plugin = DirectivePlugin(
            name='test-directives',
            directives={
                'focus': {'mounted': lambda el: el.focus()}
            }
        )
        
        assert plugin.name == 'test-directives'
        assert 'focus' in plugin.directives

    def test_filter_plugin(self):
        """Test filter plugin."""
        plugin = FilterPlugin(
            name='test-filters',
            filters={
                'reverse': lambda s: s[::-1]
            }
        )
        
        assert plugin.name == 'test-filters'
        assert 'reverse' in plugin.filters

    def test_hook_plugin(self):
        """Test hook plugin."""
        plugin = HookPlugin(
            name='test-hooks',
            hooks={
                'before_compile': lambda ast: ast
            }
        )
        
        assert plugin.name == 'test-hooks'
        assert 'before_compile' in plugin.hooks

    def test_hook_manager(self):
        """Test hook manager."""
        manager = HookManager()
        
        def test_hook():
            return "test"
        
        manager.register('test', test_hook)
        hooks = manager.get('test')
        
        assert len(hooks) == 1
        assert manager.run('test')[0] == "test"

    def test_compiler_runs_registered_hooks(self):
        registry = PluginRegistry()
        api = PluginAPI(registry)
        registry.set_api(api)
        api.register_hook("before_compile", lambda source: source.replace("Hello", "Hooked"))
        api.register_hook("after_compile", lambda code: code + "\n// plugin-complete")
        result = compile("<template><div>Hello</div></template>", plugin_registry=registry)
        assert result["success"] is True
        assert "Hooked" in result["code"]
        assert "plugin-complete" in result["code"]
