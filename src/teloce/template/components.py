"""
Component parser for Teloce templates.

Parses custom component tags and component references.
"""

import re
from typing import Optional, List, Dict, Any
from teloce.ast.nodes import ComponentNode


class ComponentParser:
    """
    Parses custom component tags.
    """
    
    def __init__(self):
        self.errors: List[str] = []
        self.components: Dict[str, str] = {}  # name -> source
    
    def parse(self, name: str, props: Dict[str, str],
              children: List = None, slots: Dict[str, List] = None) -> Optional[ComponentNode]:
        """
        Parse a component tag.
        
        Args:
            name: The component name
            props: The component props
            children: The child nodes
            slots: Named slots
            
        Returns:
            A ComponentNode or None if parsing fails.
        """
        self.errors = []
        
        if not name:
            self.errors.append("Component name is required")
            return None
        
        # Check if component is registered
        if name not in self.components:
            # Component might be imported, check PascalCase naming convention
            pass
        
        return ComponentNode(name, props or {}, children or [], slots or {})
    
    def parse_props(self, attributes: Dict[str, str]) -> Dict[str, str]:
        """
        Parse component props from attributes.
        
        Args:
            attributes: The attributes of the component tag
            
        Returns:
            A dictionary of prop name -> value.
        """
        self.errors = []
        props = {}
        
        for name, value in attributes.items():
            # Skip directives and special attributes
            if name.startswith('@') or name.startswith(':'):
                continue
            if name in ['slot', 'is', 'key']:
                continue
            
            props[name] = value
        
        return props
    
    def parse_vue_props(self, attributes: Dict[str, str]) -> Dict[str, str]:
        """
        Parse Vue-style props with colon bindings.
        
        Args:
            attributes: The attributes of the component tag
            
        Returns:
            A dictionary of prop name -> value.
        """
        self.errors = []
        props = {}
        
        for name, value in attributes.items():
            if name.startswith(':'):
                prop_name = name[1:]
                props[prop_name] = value
            elif name.startswith('@'):
                # Event binding, not a prop
                pass
            else:
                # Regular attribute as string prop
                props[name] = value
        
        return props
    
    def register_component(self, name: str, source: str):
        """
        Register a component for resolution.
        
        Args:
            name: The component name
            source: The component source file path
        """
        self.components[name] = source
    
    def resolve_component(self, name: str) -> Optional[str]:
        """
        Resolve a component by name.
        
        Args:
            name: The component name
            
        Returns:
            The component source path or None if not found.
        """
        return self.components.get(name)
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0