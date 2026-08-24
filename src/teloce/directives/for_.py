"""
For directive (<for>) for list rendering.
"""

import re
from typing import Optional, List
from teloce.directives.base import Directive, DirectiveType, DirectiveContext


class ForDirective(Directive):
    """
    Loop directive.
    
    Handles <for> for list rendering with keyed support.
    """
    
    def __init__(self):
        super().__init__(
            name='for',
            type=DirectiveType.LOOP,
            priority=30,
            description='List rendering directive'
        )
    
    def validate(self, value: str, context: DirectiveContext) -> List[str]:
        """Validate the for expression."""
        errors = []
        
        if not value or not value.strip():
            errors.append("For expression cannot be empty")
            return errors
        
        # Parse the for expression
        # Format: "item in items" or "item in items key id"
        parsed = self._parse_for_expression(value)
        if not parsed:
            errors.append(f"Invalid for expression: '{value}'")
        else:
            item, collection, key = parsed
            if not item:
                errors.append("Missing item variable in for expression")
            if not collection:
                errors.append("Missing collection in for expression")
        
        return errors
    
    def transform(self, value: str, context: DirectiveContext) -> str:
        """Transform the for expression."""
        return value.strip()
    
    def generate(self, value: str, context: DirectiveContext) -> str:
        """Generate JavaScript for the for expression."""
        parsed = self._parse_for_expression(value)
        if parsed:
            item, collection, key = parsed
            # Generate the loop structure
            if key:
                return f"for (const [{key}, {item}] of {collection}.entries())"
            else:
                return f"for (const {item} of {collection})"
        return value
    
    def _parse_for_expression(self, value: str) -> Optional[tuple]:
        """
        Parse a for expression.
        
        Returns:
            A tuple of (item, collection, key) or None if parsing fails.
        """
        value = value.strip()
        
        # Check for "item in items" format
        in_match = re.match(r'^(\w+)\s+(?:in|of)\s+(\w+)(?:\s+key\s+(\w+))?$', value)
        if in_match:
            item = in_match.group(1)
            collection = in_match.group(2)
            key = in_match.group(3) or ''
            return (item, collection, key)
        
        # Check for "(item, key) in items" format (Vue-like)
        vue_match = re.match(r'^\((\w+)\s*,\s*(\w+)\)\s+(?:in|of)\s+(\w+)$', value)
        if vue_match:
            item = vue_match.group(1)
            key = vue_match.group(2)
            collection = vue_match.group(3)
            return (item, collection, key)
        
        # Check for "item of items" format
        of_match = re.match(r'^(\w+)\s+of\s+(\w+)$', value)
        if of_match:
            item = of_match.group(1)
            collection = of_match.group(2)
            return (item, collection, '')
        
        return None