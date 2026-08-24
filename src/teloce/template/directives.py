"""
Directive parser for Teloce templates.

Parses Teloce directives like @click, :model, etc.
"""

from typing import List, Optional, Dict, Any
from teloce.ast.nodes import EventNode, BindingNode


class DirectiveParser:
    """
    Parses Teloce directives.
    """
    
    def __init__(self):
        self.errors: List[str] = []
    
    def parse_event(self, name: str, handler: str) -> Optional[EventNode]:
        """
        Parse an event directive.
        
        Args:
            name: The event name (click, submit, etc.)
            handler: The event handler expression
            
        Returns:
            An EventNode or None if parsing fails.
        """
        self.errors = []
        
        if not name:
            self.errors.append("Event name is required")
            return None
        
        if not handler:
            handler = ""
        
        return EventNode(name, handler)
    
    def parse_binding(self, name: str, value: str) -> Optional[BindingNode]:
        """
        Parse a binding directive.
        
        Args:
            name: The binding name (model, class, style, etc.)
            value: The binding value expression
            
        Returns:
            A BindingNode or None if parsing fails.
        """
        self.errors = []
        
        if not name:
            self.errors.append("Binding name is required")
            return None
        
        if not value:
            value = ""
        
        return BindingNode(name, value)
    
    def parse_all_events(self, attributes: Dict[str, str]) -> List[EventNode]:
        """
        Parse all event directives from attributes.
        
        Args:
            attributes: A dictionary of attribute name -> value
            
        Returns:
            A list of EventNode objects.
        """
        self.errors = []
        events = []
        
        for name, value in attributes.items():
            if name.startswith('@'):
                event_name = name[1:]
                handler = value
                node = self.parse_event(event_name, handler)
                if node:
                    events.append(node)
        
        return events
    
    def parse_all_bindings(self, attributes: Dict[str, str]) -> List[BindingNode]:
        """
        Parse all binding directives from attributes.
        
        Args:
            attributes: A dictionary of attribute name -> value
            
        Returns:
            A list of BindingNode objects.
        """
        self.errors = []
        bindings = []
        
        for name, value in attributes.items():
            if name.startswith(':'):
                bind_name = name[1:]
                bind_value = value
                node = self.parse_binding(bind_name, bind_value)
                if node:
                    bindings.append(node)
        
        return bindings
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0