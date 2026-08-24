"""
Slot parser for Teloce templates.

Parses <slot> directives for content projection.
"""

from typing import Optional, List, Dict
from teloce.ast.nodes import SlotNode


class SlotParser:
    """
    Parses slot directives.
    """
    
    def __init__(self):
        self.errors: List[str] = []
    
    def parse(self, name: str = "default", children: List = None) -> Optional[SlotNode]:
        """
        Parse a slot directive.
        
        Args:
            name: The slot name
            children: The child nodes (fallback content)
            
        Returns:
            A SlotNode or None if parsing fails.
        """
        self.errors = []
        
        return SlotNode(name or "default", children or [])
    
    def parse_named_slots(self, attributes: dict, children: List) -> Dict[str, List]:
        """
        Parse named slots from a component.
        
        Args:
            attributes: The attributes of the component tag
            children: The child nodes
            
        Returns:
            A dictionary of slot name -> list of nodes.
        """
        self.errors = []
        
        slots = {}
        
        # Check for slot attribute on children
        for child in children:
            if hasattr(child, 'attributes') and 'slot' in child.attributes:
                slot_name = child.attributes['slot']
                if slot_name not in slots:
                    slots[slot_name] = []
                slots[slot_name].append(child)
        
        # Default slot for remaining children
        default_children = [c for c in children if not (hasattr(c, 'attributes') and 'slot' in c.attributes)]
        if default_children:
            slots['default'] = default_children
        
        return slots
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0