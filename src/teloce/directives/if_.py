"""
If directive (<if>, <else if>, <else>) for conditional rendering.
"""

import re
from typing import Optional, List
from teloce.directives.base import Directive, DirectiveType, DirectiveContext


class IfDirective(Directive):
    """
    Conditional rendering directive.
    
    Handles <if>, <else if>, and <else> for conditional rendering.
    """
    
    def __init__(self):
        super().__init__(
            name='if',
            type=DirectiveType.CONDITIONAL,
            priority=30,
            description='Conditional rendering directive'
        )
    
    def validate(self, value: str, context: DirectiveContext) -> List[str]:
        """Validate the condition."""
        errors = []
        
        if not value or not value.strip():
            errors.append("Condition cannot be empty")
            return errors
        
        # Validate the condition
        if not self._is_valid_condition(value):
            errors.append(f"Invalid condition: '{value}'")
        
        return errors
    
    def transform(self, value: str, context: DirectiveContext) -> str:
        """Transform the condition."""
        return value.strip()
    
    def generate(self, value: str, context: DirectiveContext) -> str:
        """Generate JavaScript for the condition."""
        return value
    
    def _is_valid_condition(self, value: str) -> bool:
        """Check if the condition is valid."""
        # Allow JavaScript expressions
        return bool(value.strip())


class ElseIfDirective(IfDirective):
    def __init__(self):
        super().__init__()
        self.name = 'else-if'
        self.description = 'Else-if conditional directive'
    
    def validate(self, value: str, context: DirectiveContext) -> List[str]:
        """Validate the else-if condition."""
        errors = []
        
        if not value or not value.strip():
            errors.append("Else-if condition cannot be empty")
            return errors
        
        # Validate the condition
        if not self._is_valid_condition(value):
            errors.append(f"Invalid else-if condition: '{value}'")
        
        return errors


class ElseDirective(Directive):
    """
    Else directive.
    
    Handles <else> for conditional rendering.
    """
    
    def __init__(self):
        super().__init__(
            name='else',
            type=DirectiveType.CONDITIONAL,
            priority=25,
            description='Else conditional directive'
        )
    
    def validate(self, value: str, context: DirectiveContext) -> List[str]:
        """Validate the else directive."""
        errors = []
        
        # Else should not have a value
        if value and value.strip():
            errors.append("Else directive should not have a condition")
        
        return errors
    
    def transform(self, value: str, context: DirectiveContext) -> str:
        """Transform the else directive."""
        return "true"  # Else always executes
    
    def generate(self, value: str, context: DirectiveContext) -> str:
        """Generate JavaScript for the else directive."""
        return "true"