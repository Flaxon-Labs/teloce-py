"""
Plugin API - provides the plugin interface.

Defines the plugin API and base plugin class.
"""

from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field


@dataclass
class Plugin:
    """Base plugin class."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    license: str = "MIT"
    
    def install(self, api: 'PluginAPI') -> None:
        """Install the plugin."""
        pass
    
    def uninstall(self) -> None:
        """Uninstall the plugin."""
        pass


class PluginAPI:
    """
    Plugin API for interacting with Teloce.
    
    Provides methods for plugins to extend Teloce.
    """
    
    def __init__(self, registry: 'PluginRegistry'):
        self.registry = registry
        self._directives: Dict[str, Any] = {}
        self._filters: Dict[str, Callable] = {}
        self._hooks: Dict[str, List[Callable]] = {}
        self._components: Dict[str, Any] = {}
    
    def register_directive(self, name: str | Dict[str, Any], directive: Any = None) -> None:
        """Register a custom directive."""
        if isinstance(name, dict):
            directive = name
            name = name.get("name", "")
        self._directives[name] = directive

    def unregister_directive(self, name: str) -> None:
        self._directives.pop(name, None)
    
    def register_filter(self, name: str | Dict[str, Any], filter_func: Callable = None) -> None:
        """Register a custom filter."""
        if isinstance(name, dict):
            filter_definition = name
            name = filter_definition.get("name", "")
            filter_func = filter_definition.get("transform", filter_definition.get("filter"))
        self._filters[name] = filter_func

    def register_js_filter(self, name: str, source: str) -> None:
        """Register a filter implementation that can run in generated JS."""
        self._filters[name] = {"js": source}

    def unregister_filter(self, name: str) -> None:
        self._filters.pop(name, None)
    
    def register_component(self, name: str | Dict[str, Any], component: Any = None) -> None:
        """Register a custom component."""
        if isinstance(name, dict):
            component_definition = name
            name = component_definition.get("name", "")
            component = component_definition.get("component", component_definition)
        self._components[name] = component

    def unregister_component(self, name: str) -> None:
        self._components.pop(name, None)
    
    def register_hook(self, name: str, hook_func: Callable, priority: int = 0) -> None:
        """Register a hook."""
        if name not in self._hooks:
            self._hooks[name] = []
        self._hooks[name].append((priority, hook_func))
        # Sort by priority
        self._hooks[name].sort(key=lambda x: x[0])

    def unregister_hook(self, name: str, hook_func: Callable) -> None:
        hooks = self._hooks.get(name, [])
        self._hooks[name] = [(priority, hook) for priority, hook in hooks if hook is not hook_func]
    
    def get_directive(self, name: str) -> Optional[Any]:
        """Get a registered directive."""
        return self._directives.get(name)
    
    def get_filter(self, name: str) -> Optional[Callable]:
        """Get a registered filter."""
        return self._filters.get(name)

    def get_js_filters(self) -> Dict[str, str]:
        """Return only explicitly serializable browser filter functions."""
        return {
            name: value["js"]
            for name, value in self._filters.items()
            if isinstance(value, dict) and isinstance(value.get("js"), str)
        }
    
    def get_component(self, name: str) -> Optional[Any]:
        """Get a registered component."""
        return self._components.get(name)
    
    def get_hooks(self, name: str) -> List[Callable]:
        """Get registered hooks."""
        return [hook for _, hook in self._hooks.get(name, [])]
    
    def run_hooks(self, name: str, *args, **kwargs) -> List[Any]:
        """Run all hooks for a given name."""
        results = []
        for hook in self.get_hooks(name):
            results.append(hook(*args, **kwargs))
        return results
