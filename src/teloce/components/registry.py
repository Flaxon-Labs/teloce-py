"""
Component registry - maintains a registry of components.

Provides component registration and lookup.
"""

from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field


@dataclass
class ComponentEntry:
    """An entry in the component registry."""
    name: str
    component: Any
    source: Optional[str] = None
    is_default: bool = False
    dependencies: List[str] = field(default_factory=list)


class ComponentRegistry:
    """
    Registry for components.
    
    Manages component registration and lookup.
    """
    
    def __init__(self):
        self._components: Dict[str, ComponentEntry] = {}
        self._aliases: Dict[str, str] = {}
    
    def register(self, name: str, component: Any, 
                 source: Optional[str] = None, 
                 is_default: bool = False) -> None:
        """
        Register a component.
        
        Args:
            name: The component name
            component: The component implementation
            source: The component source path
            is_default: Whether this is the default export
        """
        self._components[name] = ComponentEntry(
            name=name,
            component=component,
            source=source,
            is_default=is_default,
        )
    
    def register_alias(self, alias: str, name: str) -> None:
        """Register an alias for a component."""
        self._aliases[alias] = name
    
    def get(self, name: str) -> Optional[Any]:
        """
        Get a component by name.
        
        Args:
            name: The component name
            
        Returns:
            The component implementation or None.
        """
        # Check aliases
        if name in self._aliases:
            name = self._aliases[name]
        
        entry = self._components.get(name)
        return entry.component if entry else None
    
    def get_entry(self, name: str) -> Optional[ComponentEntry]:
        """
        Get a component entry by name.
        
        Args:
            name: The component name
            
        Returns:
            The ComponentEntry or None.
        """
        if name in self._aliases:
            name = self._aliases[name]
        return self._components.get(name)
    
    def has(self, name: str) -> bool:
        """Check if a component is registered."""
        return name in self._components or name in self._aliases
    
    def get_all(self) -> Dict[str, Any]:
        """Get all registered components."""
        return {name: entry.component for name, entry in self._components.items()}
    
    def get_names(self) -> List[str]:
        """Get all registered component names."""
        return list(self._components.keys())
    
    def clear(self) -> None:
        """Clear all registrations."""
        self._components.clear()
        self._aliases.clear()
    
    def add_dependency(self, name: str, dependency: str) -> None:
        """Add a dependency to a component."""
        entry = self._components.get(name)
        if entry:
            if dependency not in entry.dependencies:
                entry.dependencies.append(dependency)