"""
Object filters for Teloce templates.

Provides filters for object manipulation.
"""

from typing import Any, Dict, List, Optional


class ObjectFilters:
    """Object filters for templates."""
    
    @staticmethod
    def keys(value: Dict[str, Any]) -> List[str]:
        """Get the keys of an object."""
        if not value or not isinstance(value, dict):
            return []
        return list(value.keys())
    
    @staticmethod
    def values(value: Dict[str, Any]) -> List[Any]:
        """Get the values of an object."""
        if not value or not isinstance(value, dict):
            return []
        return list(value.values())
    
    @staticmethod
    def entries(value: Dict[str, Any]) -> List[tuple]:
        """Get the entries of an object."""
        if not value or not isinstance(value, dict):
            return []
        return list(value.items())
    
    @staticmethod
    def pick(value: Dict[str, Any], *keys: str) -> Dict[str, Any]:
        """Pick specific keys from an object."""
        if not value or not isinstance(value, dict):
            return {}
        result = {}
        for key in keys:
            if key in value:
                result[key] = value[key]
        return result
    
    @staticmethod
    def omit(value: Dict[str, Any], *keys: str) -> Dict[str, Any]:
        """Omit specific keys from an object."""
        if not value or not isinstance(value, dict):
            return {}
        result = value.copy()
        for key in keys:
            result.pop(key, None)
        return result
    
    @staticmethod
    def size(value: Any) -> int:
        """Get the size of an object or array."""
        if isinstance(value, dict):
            return len(value)
        if isinstance(value, (list, tuple, set)):
            return len(value)
        if isinstance(value, str):
            return len(value)
        return 0
    
    @staticmethod
    def get_all() -> dict:
        """Get all object filters."""
        return {
            'keys': ObjectFilters.keys,
            'values': ObjectFilters.values,
            'entries': ObjectFilters.entries,
            'pick': ObjectFilters.pick,
            'omit': ObjectFilters.omit,
            'size': ObjectFilters.size,
        }
    
    @staticmethod
    def get_description(name: str) -> str:
        """Get filter description."""
        descriptions = {
            'keys': 'Get the keys of an object',
            'values': 'Get the values of an object',
            'entries': 'Get the entries of an object',
            'pick': 'Pick specific keys from an object',
            'omit': 'Omit specific keys from an object',
            'size': 'Get the size of an object or array',
        }
        return descriptions.get(name, '')