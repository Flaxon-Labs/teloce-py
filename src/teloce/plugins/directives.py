"""
Directive plugin - plugin for custom directives.

Provides a plugin for adding custom directives to Teloce.
"""

from typing import Dict, Any, Optional, Callable
from teloce.plugins.api import Plugin, PluginAPI


class DirectivePlugin(Plugin):
    """
    Plugin for adding custom directives.
    
    Example:
        plugin = DirectivePlugin(
            name="my-directives",
            directives={
                "focus": {
                    "mounted": lambda el: el.focus()
                }
            }
        )
    """
    
    def __init__(self, name: str, directives: Dict[str, Any], 
                 version: str = "1.0.0", description: str = ""):
        super().__init__(name=name, version=version, description=description)
        self.directives = directives
    
    def install(self, api: PluginAPI) -> None:
        """Install the plugin."""
        self._api = api
        for name, directive in self.directives.items():
            api.register_directive(name, directive)
    
    def uninstall(self) -> None:
        """Uninstall the plugin."""
        api = getattr(self, '_api', None)
        if api:
            for name in self.directives:
                api.unregister_directive(name)
