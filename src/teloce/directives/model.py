"""
Model directive (:model) for two-way data binding.
"""

import re
from typing import Optional, List
from teloce.directives.base import Directive, DirectiveType, DirectiveContext


class ModelDirective(Directive):
    """
    Two-way binding directive.
    
    Handles :model for input, textarea, select elements.
    """
    
    def __init__(self):
        super().__init__(
            name='model',
            type=DirectiveType.BIND,
            priority=20,
            description='Two-way data binding directive'
        )
    
    def validate(self, value: str, context: DirectiveContext) -> List[str]:
        """Validate the model binding."""
        errors = []
        
        if not value or not value.strip():
            errors.append("Model binding cannot be empty")
            return errors
        
        # Check if it's a valid variable name
        if not self._is_valid_variable(value):
            errors.append(f"Invalid model variable: '{value}'")
        
        return errors
    
    def transform(self, value: str, context: DirectiveContext) -> str:
        """Transform the model binding."""
        return value.strip()
    
    def generate(self, value: str, context: DirectiveContext) -> str:
        """Generate JavaScript for the model binding."""
        # Generate code for two-way binding
        # This will be used by the JavaScript generator
        return value
    
    def _is_valid_variable(self, value: str) -> bool:
        """Check if the variable name is valid."""
        pattern = r'^[a-zA-Z_$][a-zA-Z0-9_$]*(\.[a-zA-Z_$][a-zA-Z0-9_$]*)*$'
        return bool(re.match(pattern, value.strip()))