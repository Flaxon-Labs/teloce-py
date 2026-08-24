"""
Plugin registry - manages registered plugins.

Provides plugin registration, discovery, and management.
"""

from typing import Dict, List, Optional, Any, Type, Callable
from teloce.plugins.api import Plugin, PluginAPI


class PluginRegistry:
    """
    Registry for plugins.
    
    Manages plugin registration and lifecycle.
    """
    
    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}
        self._api: Optional[PluginAPI] = None
    
    def set_api(self, api: PluginAPI) -> None:
        """Set the plugin API."""
        self._api = api
        # Registries are often assembled before the API is attached.  Ensure
        # those already-registered plugins receive their install lifecycle.
        for plugin in self._plugins.values():
            if not getattr(plugin, '_teloce_installed', False):
                plugin.install(api)
                setattr(plugin, '_teloce_installed', True)
    
    def get_api(self) -> Optional[PluginAPI]:
        """Get the plugin API."""
        return self._api
    
    def register(self, plugin: Plugin) -> None:
        """
        Register a plugin.
        
        Args:
            plugin: The plugin to register.
        """
        if plugin.name in self._plugins:
            # Plugin already registered, skip
            return
        
        self._plugins[plugin.name] = plugin
        
        # Install the plugin
        if self._api:
            plugin.install(self._api)
            setattr(plugin, '_teloce_installed', True)
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a plugin.
        
        Args:
            name: The plugin name.
            
        Returns:
            True if the plugin was unregistered, False otherwise.
        """
        plugin = self._plugins.pop(name, None)
        if plugin:
            plugin.uninstall()
            return True
        return False
    
    def get(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name."""
        return self._plugins.get(name)
    
    def get_all(self) -> List[Plugin]:
        """Get all registered plugins."""
        return list(self._plugins.values())
    
    def has(self, name: str) -> bool:
        """Check if a plugin is registered."""
        return name in self._plugins
    
    def clear(self) -> None:
        """Clear all plugins."""
        for plugin in list(self._plugins.values()):
            plugin.uninstall()
        self._plugins.clear()
    
    def get_directives(self) -> Dict[str, Any]:
        """Get all registered directives from plugins."""
        result = {}
        for plugin in self._plugins.values():
            if hasattr(plugin, 'directives'):
                result.update(plugin.directives)
        return result
    
    def get_filters(self) -> Dict[str, Callable]:
        """Get all registered filters from plugins."""
        result = {}
        for plugin in self._plugins.values():
            if hasattr(plugin, 'filters'):
                result.update(plugin.filters)
        return result
    
    def get_hooks(self) -> Dict[str, List[Callable]]:
        """Get all registered hooks from plugins."""
        result = {}
        for plugin in self._plugins.values():
            if hasattr(plugin, 'hooks'):
                for name, hook in plugin.hooks.items():
                    if name not in result:
                        result[name] = []
                    result[name].append(hook)
        return result
