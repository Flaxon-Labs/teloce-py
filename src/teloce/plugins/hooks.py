"""
Hooks plugin - plugin for lifecycle hooks.

Provides a plugin for adding lifecycle hooks to Teloce.
"""

from typing import Any, Dict, List, Callable
from dataclasses import dataclass
from teloce.plugins.api import Plugin, PluginAPI


@dataclass
class Hook:
    """A lifecycle hook."""
    name: str
    handler: Callable
    priority: int = 0


class HookPlugin(Plugin):
    """
    Plugin for adding lifecycle hooks.
    
    Example:
        plugin = HookPlugin(
            name="my-hooks",
            hooks={
                "before_compile": lambda ast: ast,
                "after_compile": lambda js: js
            }
        )
    """
    
    def __init__(self, name: str, hooks: Dict[str, Callable],
                 version: str = "1.0.0", description: str = ""):
        super().__init__(name=name, version=version, description=description)
        self.hooks = hooks
    
    def install(self, api: PluginAPI) -> None:
        """Install the plugin."""
        self._api = api
        for name, handler in self.hooks.items():
            api.register_hook(name, handler)
    
    def uninstall(self) -> None:
        """Uninstall the plugin."""
        api = getattr(self, '_api', None)
        if api:
            for name, handler in self.hooks.items():
                api.unregister_hook(name, handler)


class HookManager:
    """
    Manages hooks for the plugin system.
    """
    
    def __init__(self):
        self._hooks: Dict[str, List[tuple]] = {}
    
    def register(self, name: str, handler: Callable, priority: int = 0) -> None:
        """Register a hook."""
        if name not in self._hooks:
            self._hooks[name] = []
        self._hooks[name].append((priority, handler))
        self._hooks[name].sort(key=lambda x: x[0])
    
    def get(self, name: str) -> List[Callable]:
        """Get all hooks for a given name."""
        return [handler for _, handler in self._hooks.get(name, [])]
    
    def run(self, name: str, *args, **kwargs) -> List[Any]:
        """Run all hooks for a given name."""
        results = []
        for handler in self.get(name):
            results.append(handler(*args, **kwargs))
        return results
    
    def clear(self) -> None:
        """Clear all hooks."""
        self._hooks.clear()
