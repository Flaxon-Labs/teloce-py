"""
Filter plugin - plugin for custom filters.

Provides a plugin for adding custom filters to Teloce.
"""

from typing import Dict, Callable, Optional
from teloce.plugins.api import Plugin, PluginAPI


class FilterPlugin(Plugin):
    """
    Plugin for adding custom filters.
    
    Example:
        plugin = FilterPlugin(
            name="my-filters",
            filters={
                "reverse": lambda s: s[::-1],
                "truncate": lambda s, n: s[:n]
            }
        )
    """
    
    def __init__(self, name: str, filters: Dict[str, Callable],
                 version: str = "1.0.0", description: str = ""):
        super().__init__(name=name, version=version, description=description)
        self.filters = filters
    
    def install(self, api: PluginAPI) -> None:
        """Install the plugin."""
        self._api = api
        for name, filter_func in self.filters.items():
            api.register_filter(name, filter_func)
    
    def uninstall(self) -> None:
        """Uninstall the plugin."""
        api = getattr(self, '_api', None)
        if api:
            for name in self.filters:
                api.unregister_filter(name)
