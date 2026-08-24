"""
Base directive classes and types.

Defines the core directive interfaces and base implementations.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable, Union
from enum import Enum, auto
import re


class DirectiveType(Enum):
    """Types of directives."""
    EVENT = auto()
    BIND = auto()
    CONDITIONAL = auto()
    LOOP = auto()
    SLOT = auto()
    COMPONENT = auto()
    CUSTOM = auto()


@dataclass
class DirectiveContext:
    """
    Context for directive processing.
    """
    source: str = ""
    line: int = 0
    column: int = 0
    component_name: str = ""
    component_data: Dict[str, Any] = field(default_factory=dict)
    component_methods: Dict[str, str] = field(default_factory=dict)
    component_computed: Dict[str, str] = field(default_factory=dict)
    imports: List[str] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
    
    def get_option(self, key: str, default: Any = None) -> Any:
        """Get an option value."""
        return self.options.get(key, default)


@dataclass
class Directive:
    """
    Base directive class.
    """
    name: str
    type: DirectiveType
    priority: int = 0
    description: str = ""
    
    def transform(self, value: str, context: DirectiveContext) -> str:
        """
        Transform the directive value.
        
        Args:
            value: The raw directive value
            context: The directive context
            
        Returns:
            The transformed value.
        """
        return value
    
    def validate(self, value: str, context: DirectiveContext) -> List[str]:
        """
        Validate the directive value.
        
        Args:
            value: The raw directive value
            context: The directive context
            
        Returns:
            A list of validation errors.
        """
        return []
    
    def generate(self, value: str, context: DirectiveContext) -> str:
        """
        Generate JavaScript code for the directive.
        
        Args:
            value: The raw directive value
            context: The directive context
            
        Returns:
            The generated JavaScript code.
        """
        return value


class DirectiveHandler:
    """
    Handles directive processing.
    """
    
    def __init__(self):
        self.directives: Dict[str, Directive] = {}
    
    def register(self, directive: Directive):
        """Register a directive."""
        self.directives[directive.name] = directive
    
    def get(self, name: str) -> Optional[Directive]:
        """Get a directive by name."""
        return self.directives.get(name)
    
    def process(self, name: str, value: str, context: DirectiveContext) -> Optional[str]:
        """
        Process a directive.
        
        Args:
            name: The directive name
            value: The directive value
            context: The directive context
            
        Returns:
            The processed value or None if the directive is not found.
        """
        directive = self.get(name)
        if not directive:
            return None
        
        # Validate
        errors = directive.validate(value, context)
        if errors:
            raise ValueError(f"Directive validation failed: {', '.join(errors)}")
        
        # Transform
        transformed = directive.transform(value, context)
        
        # Generate
        return directive.generate(transformed, context)