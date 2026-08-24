"""
Loop parser for Teloce templates.

Parses <for> directives.
"""

import re
from typing import Optional, List, Tuple
from teloce.ast.nodes import ForNode


class LoopParser:
    """
    Parses for loop directives.
    """
    
    def __init__(self):
        self.errors: List[str] = []
    
    def parse(self, attributes: dict, children: List) -> Optional[ForNode]:
        """
        Parse a for loop directive.
        
        Args:
            attributes: The attributes of the for tag
            children: The child nodes of the for tag
            
        Returns:
            A ForNode or None if parsing fails.
        """
        self.errors = []
        
        # Extract attributes
        item = attributes.get('item', '')
        collection = attributes.get('in', '') or attributes.get('collection', '')
        key = attributes.get('key', '')
        
        # Also handle shorthand: <for item in items>
        # The lexer may not parse this correctly, so check the raw attributes
        if not item and not collection:
            # Try to parse from the raw attribute string
            item, collection, key = self._parse_for_attribute(attributes)
        
        if not item:
            self.errors.append("Missing 'item' attribute in for loop")
            return None
        
        if not collection:
            self.errors.append("Missing 'collection' attribute in for loop")
            return None
        
        return ForNode(item, collection, key, children or [])
    
    def _parse_for_attribute(self, attributes: dict) -> Tuple[str, str, str]:
        """
        Parse the for attribute from various formats.
        
        Returns:
            A tuple of (item, collection, key).
        """
        item = ''
        collection = ''
        key = ''
        
        # Check for item and collection in attributes
        for attr_name, attr_value in attributes.items():
            if attr_name == 'item':
                item = attr_value
            elif attr_name == 'in' or attr_name == 'collection':
                collection = attr_value
            elif attr_name == 'key':
                key = attr_value
        
        # If we still don't have both, try to parse from a combined attribute
        if (not item or not collection) and 'for' in attributes:
            for_attr = attributes['for']
            # Parse: "item in items" or "item of items"
            match = re.match(r'(\w+)\s+(?:in|of)\s+(\w+)', for_attr)
            if match:
                item = match.group(1)
                collection = match.group(2)
            
            # Also check for key: "item in items key id"
            key_match = re.search(r'key\s+(\w+)', for_attr)
            if key_match:
                key = key_match.group(1)
        
        return item, collection, key
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0