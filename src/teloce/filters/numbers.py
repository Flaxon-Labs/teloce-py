"""
Number filters for Teloce templates.

Provides filters for number manipulation and formatting.
"""

from typing import Any, Optional


class NumberFilters:
    """Number filters for templates."""
    
    @staticmethod
    def currency(value: float, symbol: str = '$', decimals: int = 2) -> str:
        """Format a number as currency."""
        if value is None or value == '':
            return ''
        return f"{symbol}{value:.{decimals}f}"
    
    @staticmethod
    def percent(value: float, decimals: int = 0) -> str:
        """Format a number as percentage."""
        if value is None or value == '':
            return ''
        return f"{value * 100:.{decimals}f}%"
    
    @staticmethod
    def number(value: float) -> str:
        """Format a number with commas."""
        if value is None or value == '':
            return ''
        return f"{value:,}"
    
    @staticmethod
    def decimal(value: float, places: int = 2) -> str:
        """Format a number with decimal places."""
        if value is None or value == '':
            return ''
        return f"{value:.{places}f}"
    
    @staticmethod
    def round(value: float) -> int:
        """Round a number."""
        if value is None or value == '':
            return 0
        return round(value)
    
    @staticmethod
    def floor(value: float) -> int:
        """Floor a number."""
        if value is None or value == '':
            return 0
        import math
        return math.floor(value)
    
    @staticmethod
    def ceil(value: float) -> int:
        """Ceil a number."""
        if value is None or value == '':
            return 0
        import math
        return math.ceil(value)
    
    @staticmethod
    def abs(value: float) -> float:
        """Absolute value."""
        if value is None or value == '':
            return 0
        return abs(value)
    
    @staticmethod
    def get_all() -> dict:
        """Get all number filters."""
        return {
            'currency': NumberFilters.currency,
            'percent': NumberFilters.percent,
            'number': NumberFilters.number,
            'decimal': NumberFilters.decimal,
            'round': NumberFilters.round,
            'floor': NumberFilters.floor,
            'ceil': NumberFilters.ceil,
            'abs': NumberFilters.abs,
        }
    
    @staticmethod
    def get_description(name: str) -> str:
        """Get filter description."""
        descriptions = {
            'currency': 'Format as currency',
            'percent': 'Format as percentage',
            'number': 'Format with commas',
            'decimal': 'Format with decimal places',
            'round': 'Round number',
            'floor': 'Floor number',
            'ceil': 'Ceil number',
            'abs': 'Absolute value',
        }
        return descriptions.get(name, '')