"""
Event directive (@click, @submit, @input, etc.).
"""

from typing import Optional, List
import re
from teloce.directives.base import Directive, DirectiveType, DirectiveContext


class EventDirective(Directive):
    """
    Event binding directive.
    
    Handles @click, @submit, @input, @change, @keyup, etc.
    """
    
    # Supported events
    EVENTS = {
        'click', 'submit', 'input', 'change', 'keyup', 'keydown',
        'focus', 'blur', 'mouseenter', 'mouseleave', 'mouseover',
        'mouseout', 'mousedown', 'mouseup', 'scroll', 'resize',
        'drag', 'drop', 'load', 'error', 'abort'
    }
    
    def __init__(self):
        super().__init__(
            name='event',
            type=DirectiveType.EVENT,
            priority=10,
            description='Event binding directive'
        )
    
    def validate(self, value: str, context: DirectiveContext) -> List[str]:
        """Validate the event handler."""
        errors = []
        
        if not value or not value.strip():
            errors.append("Event handler cannot be empty")
            return errors
        
        # Check if it's a valid method name
        if not self._is_valid_handler(value):
            errors.append(f"Invalid event handler: '{value}'")
        
        return errors
    
    def transform(self, value: str, context: DirectiveContext) -> str:
        """Transform the event handler."""
        # Remove any whitespace
        value = value.strip()
        
        # Handle method calls with parameters
        # e.g., "handleClick(param1, param2)" -> "handleClick"
        if '(' in value and ')' in value:
            method_name = value[:value.index('(')].strip()
            return method_name
        
        return value
    
    def generate(self, value: str, context: DirectiveContext) -> str:
        """Generate JavaScript for the event binding."""
        # Return the handler as-is
        return value
    
    def _is_valid_handler(self, value: str) -> bool:
        """Check if the handler is valid."""
        # Allow method names with optional parameters
        pattern = r'^[a-zA-Z_$][a-zA-Z0-9_$]*(\s*\([^)]*\))?$'
        return bool(re.match(pattern, value.strip()))


# Specific event directives
class ClickDirective(EventDirective):
    def __init__(self):
        super().__init__()
        self.name = '@click'
        self.description = 'Click event binding'


class SubmitDirective(EventDirective):
    def __init__(self):
        super().__init__()
        self.name = '@submit'
        self.description = 'Submit event binding'


class InputDirective(EventDirective):
    def __init__(self):
        super().__init__()
        self.name = '@input'
        self.description = 'Input event binding'


class ChangeDirective(EventDirective):
    def __init__(self):
        super().__init__()
        self.name = '@change'
        self.description = 'Change event binding'


class KeyupDirective(EventDirective):
    def __init__(self):
        super().__init__()
        self.name = '@keyup'
        self.description = 'Keyup event binding'


class KeydownDirective(EventDirective):
    def __init__(self):
        super().__init__()
        self.name = '@keydown'
        self.description = 'Keydown event binding'


class FocusDirective(EventDirective):
    def __init__(self):
        super().__init__()
        self.name = '@focus'
        self.description = 'Focus event binding'


class BlurDirective(EventDirective):
    def __init__(self):
        super().__init__()
        self.name = '@blur'
        self.description = 'Blur event binding'
