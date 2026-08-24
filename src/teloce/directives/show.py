"""
Show directive (:show, :hide) for conditional visibility.
"""

import re
from typing import Optional, List
from teloce.directives.base import Directive, DirectiveType, DirectiveContext


class ShowDirective(Directive):
    """
    Show/hide directive.
    
    Handles :show and :hide for conditional visibility.
    """
    
    def __init__(self):
        super().__init__(
            name='show',
            type=DirectiveType.BIND,
            priority=15,
            description='Conditional show/hide directive'
        )
    
    def validate(self, value: str, context: DirectiveContext) -> List[str]:
        """Validate the show expression."""
        errors = []
        
        if not value or not value.strip():
            errors.append("Show expression cannot be empty")
            return errors
        
        # Validate the expression
        if not self._is_valid_expression(value):
            errors.append(f"Invalid show expression: '{value}'")
        
        return errors
    
    def transform(self, value: str, context: DirectiveContext) -> str:
        """Transform the show expression."""
        return value.strip()
    
    def generate(self, value: str, context: DirectiveContext) -> str:
        """Generate JavaScript for the show expression."""
        return value
    
    def _is_valid_expression(self, value: str) -> bool:
        """Check if the expression is valid."""
        # Allow JavaScript expressions
        return bool(value.strip())


class HideDirective(ShowDirective):
    def __init__(self):
        super().__init__()
        self.name = 'hide'
        self.description = 'Conditional hide directive'
    
    def generate(self, value: str, context: DirectiveContext) -> str:
        """Generate JavaScript for the hide expression."""
        # Hide is the inverse of show
        return f"!({value})"