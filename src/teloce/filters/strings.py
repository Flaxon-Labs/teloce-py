"""
String filters for Teloce templates.

Provides filters for string manipulation.
"""

from typing import Any, List, Optional
import re


class StringFilters:
    """String filters for templates."""
    
    @staticmethod
    def capitalize(value: str) -> str:
        """Capitalize the first letter of a string."""
        if not value:
            return ''
        return value[0].upper() + value[1:].lower()
    
    @staticmethod
    def uppercase(value: str) -> str:
        """Convert string to uppercase."""
        if not value:
            return ''
        return value.upper()
    
    @staticmethod
    def lowercase(value: str) -> str:
        """Convert string to lowercase."""
        if not value:
            return ''
        return value.lower()
    
    @staticmethod
    def trim(value: str) -> str:
        """Trim whitespace from both ends."""
        if not value:
            return ''
        return value.strip()
    
    @staticmethod
    def truncate(value: str, length: int = 30, suffix: str = '...') -> str:
        """Truncate a string to a specified length."""
        if not value:
            return ''
        if len(value) <= length:
            return value
        return value[:length].rstrip() + suffix
    
    @staticmethod
    def slugify(value: str) -> str:
        """Convert a string to a URL-friendly slug."""
        if not value:
            return ''
        # Remove special characters and convert to lowercase
        slug = re.sub(r'[^\w\s-]', '', value)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.lower().strip('-')
    
    @staticmethod
    def kebab_case(value: str) -> str:
        """Convert to kebab-case."""
        if not value:
            return ''
        # Convert camelCase and spaces to kebab-case
        s = re.sub(r'(?<=[a-z0-9])([A-Z])', r'-\1', value)
        s = re.sub(r'[_\s]+', '-', s)
        return s.lower().strip('-')
    
    @staticmethod
    def camel_case(value: str) -> str:
        """Convert to camelCase."""
        if not value:
            return ''
        # Remove non-alphanumeric characters
        s = re.sub(r'[^a-zA-Z0-9\s]', ' ', value)
        # Split and capitalize
        words = s.split()
        if not words:
            return ''
        result = words[0].lower()
        for word in words[1:]:
            result += word.capitalize()
        return result
    
    @staticmethod
    def snake_case(value: str) -> str:
        """Convert to snake_case."""
        if not value:
            return ''
        s = re.sub(r'(?<=[a-z0-9])([A-Z])', r'_\1', value)
        s = re.sub(r'[-\s]+', '_', s)
        return s.lower().strip('_')
    
    @staticmethod
    def start_case(value: str) -> str:
        """Convert to Start Case."""
        if not value:
            return ''
        s = re.sub(r'[^a-zA-Z0-9\s]', ' ', value)
        words = s.split()
        return ' '.join(word.capitalize() for word in words)
    
    @staticmethod
    def escape_html(value: str) -> str:
        """Escape HTML entities."""
        if not value:
            return ''
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#039;",
            ">": "&gt;",
            "<": "&lt;",
        }
        return "".join(html_escape_table.get(c, c) for c in value)
    
    @staticmethod
    def unescape_html(value: str) -> str:
        """Unescape HTML entities."""
        if not value:
            return ''
        html_unescape_table = {
            "&amp;": "&",
            "&quot;": '"',
            "&#039;": "'",
            "&gt;": ">",
            "&lt;": "<",
        }
        result = value
        for entity, char in html_unescape_table.items():
            result = result.replace(entity, char)
        return result
    
    @staticmethod
    def get_all() -> dict:
        """Get all string filters."""
        return {
            'capitalize': StringFilters.capitalize,
            'uppercase': StringFilters.uppercase,
            'lowercase': StringFilters.lowercase,
            'trim': StringFilters.trim,
            'truncate': StringFilters.truncate,
            'slugify': StringFilters.slugify,
            'kebabCase': StringFilters.kebab_case,
            'camelCase': StringFilters.camel_case,
            'snakeCase': StringFilters.snake_case,
            'startCase': StringFilters.start_case,
            'escape': StringFilters.escape_html,
            'unescape': StringFilters.unescape_html,
        }
    
    @staticmethod
    def get_description(name: str) -> str:
        """Get filter description."""
        descriptions = {
            'capitalize': 'Capitalize the first letter of a string',
            'uppercase': 'Convert string to uppercase',
            'lowercase': 'Convert string to lowercase',
            'trim': 'Trim whitespace from both ends',
            'truncate': 'Truncate a string to a specified length',
            'slugify': 'Convert to a URL-friendly slug',
            'kebabCase': 'Convert to kebab-case',
            'camelCase': 'Convert to camelCase',
            'snakeCase': 'Convert to snake_case',
            'startCase': 'Convert to Start Case',
            'escape': 'Escape HTML entities',
            'unescape': 'Unescape HTML entities',
        }
        return descriptions.get(name, '')