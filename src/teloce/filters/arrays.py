"""
Array filters for Teloce templates.

Provides filters for array manipulation.
"""

from typing import Any, List, Optional, Callable
from collections import defaultdict


class ArrayFilters:
    """Array filters for templates."""
    
    @staticmethod
    def join(value: List[Any], separator: str = ', ') -> str:
        """Join array elements with a separator."""
        if not value:
            return ''
        return separator.join(str(item) for item in value)
    
    @staticmethod
    def first(value: List[Any]) -> Optional[Any]:
        """Get the first element of an array."""
        if not value:
            return None
        return value[0]
    
    @staticmethod
    def last(value: List[Any]) -> Optional[Any]:
        """Get the last element of an array."""
        if not value:
            return None
        return value[-1]
    
    @staticmethod
    def pluck(value: List[dict], key: str) -> List[Any]:
        """Extract a property from an array of objects."""
        if not value:
            return []
        return [item.get(key) for item in value if isinstance(item, dict)]
    
    @staticmethod
    def where(value: List[dict], key: str, operator: str, compare: Any) -> List[dict]:
        """Filter an array of objects by a property."""
        if not value:
            return []
        
        operators = {
            'eq': lambda a, b: a == b,
            'neq': lambda a, b: a != b,
            'gt': lambda a, b: a > b,
            'gte': lambda a, b: a >= b,
            'lt': lambda a, b: a < b,
            'lte': lambda a, b: a <= b,
            'in': lambda a, b: a in b,
            'nin': lambda a, b: a not in b,
        }
        
        op_func = operators.get(operator)
        if not op_func:
            return value
        
        return [item for item in value if isinstance(item, dict) and op_func(item.get(key), compare)]
    
    @staticmethod
    def order_by(value: List[dict], key: str, direction: str = 'asc') -> List[dict]:
        """Sort an array of objects by a property."""
        if not value:
            return []
        
        reverse = direction.lower() == 'desc'
        return sorted(value, key=lambda x: x.get(key) if isinstance(x, dict) else '', reverse=reverse)
    
    @staticmethod
    def group_by(value: List[dict], key: str) -> dict:
        """Group an array of objects by a property."""
        if not value:
            return {}
        
        result = defaultdict(list)
        for item in value:
            if isinstance(item, dict):
                result[item.get(key)].append(item)
        
        return dict(result)
    
    @staticmethod
    def get_all() -> dict:
        """Get all array filters."""
        return {
            'join': ArrayFilters.join,
            'first': ArrayFilters.first,
            'last': ArrayFilters.last,
            'pluck': ArrayFilters.pluck,
            'where': ArrayFilters.where,
            'orderBy': ArrayFilters.order_by,
            'groupBy': ArrayFilters.group_by,
        }
    
    @staticmethod
    def get_description(name: str) -> str:
        """Get filter description."""
        descriptions = {
            'join': 'Join array elements with a separator',
            'first': 'Get the first element',
            'last': 'Get the last element',
            'pluck': 'Extract a property from an array of objects',
            'where': 'Filter an array of objects by a property',
            'orderBy': 'Sort an array of objects by a property',
            'groupBy': 'Group an array of objects by a property',
        }
        return descriptions.get(name, '')