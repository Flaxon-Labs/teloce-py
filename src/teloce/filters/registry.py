"""
Filter registry - manages template filters.

Provides registration and lookup for template filters.
"""

from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field


@dataclass
class Filter:
    """A template filter."""
    name: str
    func: Callable[[Any], Any]
    description: str = ""
    examples: List[str] = field(default_factory=list)
    js: Optional[str] = None


class FilterRegistry:
    """
    Registry for template filters.
    
    Manages filter registration and lookup.
    """
    
    def __init__(self):
        self._filters: Dict[str, Filter] = {}
    
    def register(self, filter: Filter) -> None:
        """Register a filter."""
        self._filters[filter.name] = filter
    
    def register_func(self, name: str, func: Callable[[Any], Any], 
                      description: str = "") -> None:
        """Register a filter function."""
        self._filters[name] = Filter(name=name, func=func, description=description)

    def register_js(self, name: str, source: str, description: str = "") -> None:
        """Register a browser implementation as a JavaScript expression."""
        self._filters[name] = Filter(name=name, func=lambda value: value, description=description, js=source)

    def get_js_filters(self) -> Dict[str, str]:
        return {name: item.js for name, item in self._filters.items() if item.js}
    
    def get(self, name: str) -> Optional[Filter]:
        """Get a filter by name."""
        return self._filters.get(name)
    
    def get_func(self, name: str) -> Optional[Callable[[Any], Any]]:
        """Get a filter function by name."""
        filter = self.get(name)
        return filter.func if filter else None
    
    def has(self, name: str) -> bool:
        """Check if a filter exists."""
        return name in self._filters
    
    def get_all(self) -> Dict[str, Filter]:
        """Get all registered filters."""
        return self._filters.copy()
    
    def get_names(self) -> List[str]:
        """Get all registered filter names."""
        return list(self._filters.keys())
    
    def clear(self) -> None:
        """Clear all registrations."""
        self._filters.clear()
    
    def register_builtins(self) -> None:
        """Register all built-in filters."""
        from teloce.filters.strings import StringFilters
        from teloce.filters.numbers import NumberFilters
        from teloce.filters.dates import DateFilters
        from teloce.filters.arrays import ArrayFilters
        from teloce.filters.objects import ObjectFilters
        
        # String filters
        for name, func in StringFilters.get_all().items():
            self.register_func(name, func, StringFilters.get_description(name))
        
        # Number filters
        for name, func in NumberFilters.get_all().items():
            self.register_func(name, func, NumberFilters.get_description(name))
        
        # Date filters
        for name, func in DateFilters.get_all().items():
            self.register_func(name, func, DateFilters.get_description(name))
        
        # Array filters
        for name, func in ArrayFilters.get_all().items():
            self.register_func(name, func, ArrayFilters.get_description(name))
        
        # Object filters
        for name, func in ObjectFilters.get_all().items():
            self.register_func(name, func, ObjectFilters.get_description(name))
