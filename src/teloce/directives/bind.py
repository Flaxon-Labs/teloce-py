"""
Bind directive (:class, :style, :disabled, etc.).

This module provides directives for attribute binding in Teloce templates.
"""

import re
from typing import Optional, List, Set
from teloce.directives.base import Directive, DirectiveType, DirectiveContext


class BindDirective(Directive):
    """
    Attribute binding directive.
    
    Handles :class, :style, :disabled, :checked, :value, :href, :src, etc.
    """
    
    # Supported bindings
    BINDINGS = {
        'class': 'class',
        'style': 'style',
        'disabled': 'disabled',
        'checked': 'checked',
        'value': 'value',
        'href': 'href',
        'src': 'src',
        'id': 'id',
        'title': 'title',
        'alt': 'alt',
        'width': 'width',
        'height': 'height',
        'data': 'data',
        'aria': 'aria',
    }
    
    # JavaScript keywords that are not allowed in bind expressions
    FORBIDDEN_KEYWORDS: Set[str] = {
        'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break',
        'continue', 'return', 'function', 'class', 'let', 'const', 'var',
        'import', 'export', 'default', 'new', 'delete', 'void', 'typeof',
        'instanceof', 'in', 'with', 'yield', 'await', 'async', 'try',
        'catch', 'finally', 'throw', 'debugger', 'super', 'extends'
    }
    
    def __init__(self):
        super().__init__(
            name='bind',
            type=DirectiveType.BIND,
            priority=15,
            description='Attribute binding directive'
        )
    
    def validate(self, value: str, context: DirectiveContext) -> List[str]:
        """Validate the bind expression."""
        errors = []
        
        if not value or not value.strip():
            errors.append("Bind expression cannot be empty")
            return errors
        
        # Validate the expression
        if not self._is_valid_expression(value):
            errors.append(f"Invalid bind expression: '{value}'")
        
        return errors
    
    def transform(self, value: str, context: DirectiveContext) -> str:
        """Transform the bind expression."""
        return value.strip()
    
    def generate(self, value: str, context: DirectiveContext) -> str:
        """Generate JavaScript for the bind expression."""
        return value
    
    def _is_valid_expression(self, value: str) -> bool:
        """
        Check if the expression is valid.
        
        This performs a quick validation pass. The full expression parser
        handles complex validation and AST building.
        """
        if not value or not value.strip():
            return False
        
        value = value.strip()
        
        # Check for balanced parentheses, brackets, and braces
        if not self._is_balanced(value):
            return False
        
        # Check for balanced quotes
        if not self._is_quotes_balanced(value):
            return False
        
        # Check for forbidden keywords at the top level
        if self._has_forbidden_keyword(value):
            return False
        
        return True
    
    def _is_balanced(self, value: str) -> bool:
        """Check if parentheses, brackets, and braces are balanced."""
        stack = []
        pairs = {'(': ')', '[': ']', '{': '}'}
        in_string = False
        string_char = None
        escape = False
        
        for char in value:
            if escape:
                escape = False
                continue
            
            if char == '\\':
                escape = True
                continue
            
            if in_string:
                if char == string_char:
                    in_string = False
                    string_char = None
                continue
            
            if char in ('"', "'"):
                in_string = True
                string_char = char
                continue
            
            if char in pairs:
                stack.append(char)
            elif char in pairs.values():
                if not stack:
                    return False
                opening = stack.pop()
                if pairs[opening] != char:
                    return False
        
        return len(stack) == 0
    
    def _is_quotes_balanced(self, value: str) -> bool:
        """Check if quotes are balanced."""
        in_single = False
        in_double = False
        escape = False
        
        for char in value:
            if escape:
                escape = False
                continue
            
            if char == '\\':
                escape = True
                continue
            
            if char == "'" and not in_double:
                in_single = not in_single
            elif char == '"' and not in_single:
                in_double = not in_double
        
        return not in_single and not in_double
    
    def _has_forbidden_keyword(self, value: str) -> bool:
        """
        Check if the expression contains forbidden JavaScript keywords.
        
        This prevents statements like `if`, `for`, `while` from being used
        in bind expressions, which are expressions not statements.
        """
        # Strip quotes and string literals before checking
        cleaned = value
        in_string = False
        string_char = None
        escape = False
        result = []
        
        for char in cleaned:
            if escape:
                escape = False
                result.append(char)
                continue
            
            if char == '\\':
                escape = True
                result.append(char)
                continue
            
            if in_string:
                result.append(char)
                if char == string_char:
                    in_string = False
                    string_char = None
                continue
            
            if char in ('"', "'"):
                in_string = True
                string_char = char
                result.append(char)
                continue
            
            result.append(char)
        
        cleaned = ''.join(result)
        
        # Check for forbidden keywords as whole words
        for keyword in self.FORBIDDEN_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, cleaned):
                return True
        
        return False


class ClassBindDirective(BindDirective):
    """Class binding directive (:class)."""
    
    def __init__(self):
        super().__init__()
        self.name = ':class'
        self.description = 'Class binding directive'
    
    def validate(self, value: str, context: DirectiveContext) -> List[str]:
        """Validate the class expression."""
        errors = []
        
        if not value or not value.strip():
            errors.append("Class expression cannot be empty")
            return errors
        
        # Check for object syntax: { active: isActive }
        # Check for array syntax: ['active', 'inactive']
        # Check for string: 'active-class'
        # Check for variable: className
        if not self._is_valid_class_expression(value):
            errors.append(f"Invalid class expression: '{value}'")
        
        return errors
    
    def transform(self, value: str, context: DirectiveContext) -> str:
        """Transform the class expression."""
        value = value.strip()
        
        # If it's a string literal, wrap it properly
        if self._is_string_literal(value):
            return value
        
        # If it's a variable, return as-is
        if self._is_identifier(value):
            return value
        
        # Otherwise, treat as an expression
        return value
    
    def generate(self, value: str, context: DirectiveContext) -> str:
        """Generate JavaScript for the class expression."""
        value = value.strip()
        
        # Generate appropriate code based on the expression type
        if self._is_string_literal(value):
            # String literal: 'active-class'
            return value
        
        if self._is_identifier(value):
            # Variable: className
            return value
        
        if value.startswith('{') and value.endswith('}'):
            # Object syntax: { active: isActive }
            return value
        
        if value.startswith('[') and value.endswith(']'):
            # Array syntax: ['active', 'inactive']
            return value
        
        # Default: return as-is
        return value
    
    def _is_valid_class_expression(self, value: str) -> bool:
        """Check if the class expression is valid."""
        value = value.strip()
        
        # Object syntax: { active: isActive }
        if value.startswith('{') and value.endswith('}'):
            return self._is_valid_object_expression(value[1:-1])
        
        # Array syntax: ['active', 'inactive']
        if value.startswith('[') and value.endswith(']'):
            return self._is_valid_array_expression(value[1:-1])
        
        # String literal: 'active-class'
        if self._is_string_literal(value):
            return True
        
        # Variable: className
        if self._is_identifier(value):
            return True
        
        return False
    
    def _is_valid_object_expression(self, value: str) -> bool:
        """Check if an object expression is valid."""
        if not value.strip():
            return False
        
        # Check for key: value pairs
        parts = value.split(',')
        for part in parts:
            part = part.strip()
            if not part:
                return False
            
            # Check for key: value format
            if ':' not in part:
                return False
            
            key, val = part.split(':', 1)
            key = key.strip()
            val = val.strip()
            
            if not key or not val:
                return False
            
            # Key should be a valid identifier or string
            if not (self._is_identifier(key) or self._is_string_literal(key)):
                return False
        
        return True
    
    def _is_valid_array_expression(self, value: str) -> bool:
        """Check if an array expression is valid."""
        if not value.strip():
            return True
        
        parts = value.split(',')
        for part in parts:
            part = part.strip()
            if not part:
                return False
            
            # Each element should be a string literal or identifier
            if not (self._is_string_literal(part) or self._is_identifier(part)):
                return False
        
        return True
    
    def _is_string_literal(self, value: str) -> bool:
        """Check if the value is a string literal."""
        value = value.strip()
        return (value.startswith("'") and value.endswith("'")) or \
               (value.startswith('"') and value.endswith('"'))
    
    def _is_identifier(self, value: str) -> bool:
        """Check if the value is a valid JavaScript identifier."""
        value = value.strip()
        return bool(re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$', value))


class StyleBindDirective(BindDirective):
    """Style binding directive (:style)."""
    
    def __init__(self):
        super().__init__()
        self.name = ':style'
        self.description = 'Style binding directive'
    
    def validate(self, value: str, context: DirectiveContext) -> List[str]:
        """Validate the style expression."""
        errors = []
        
        if not value or not value.strip():
            errors.append("Style expression cannot be empty")
            return errors
        
        # Check for object syntax: { color: textColor }
        if not self._is_valid_style_expression(value):
            errors.append(f"Invalid style expression: '{value}'")
        
        return errors
    
    def transform(self, value: str, context: DirectiveContext) -> str:
        """Transform the style expression."""
        value = value.strip()
        
        # If it's a variable, return as-is
        if self._is_identifier(value):
            return value
        
        # Otherwise, treat as an object expression
        return value
    
    def generate(self, value: str, context: DirectiveContext) -> str:
        """Generate JavaScript for the style expression."""
        value = value.strip()
        
        # Variable: styleObject
        if self._is_identifier(value):
            return value
        
        # Object syntax: { color: textColor }
        if value.startswith('{') and value.endswith('}'):
            return value
        
        # Default: return as-is
        return value
    
    def _is_valid_style_expression(self, value: str) -> bool:
        """Check if the style expression is valid."""
        value = value.strip()
        
        # Object syntax: { color: textColor, fontSize: textSize + 'px' }
        if value.startswith('{') and value.endswith('}'):
            return self._is_valid_object_expression(value[1:-1])
        
        # Variable: styleObject
        if self._is_identifier(value):
            return True
        
        return False
    
    def _is_valid_object_expression(self, value: str) -> bool:
        """Check if an object expression is valid."""
        if not value.strip():
            return False
        
        parts = self._split_by_comma_outside_quotes(value)
        for part in parts:
            part = part.strip()
            if not part:
                return False
            
            # Check for key: value format
            if ':' not in part:
                return False
            
            key, val = part.split(':', 1)
            key = key.strip()
            val = val.strip()
            
            if not key or not val:
                return False
            
            # Key should be a valid CSS property
            if not self._is_valid_css_property(key):
                return False
        
        return True
    
    def _split_by_comma_outside_quotes(self, value: str) -> List[str]:
        """Split by comma, ignoring commas inside quotes."""
        parts = []
        current = []
        in_string = False
        string_char = None
        escape = False
        
        for char in value:
            if escape:
                escape = False
                current.append(char)
                continue
            
            if char == '\\':
                escape = True
                current.append(char)
                continue
            
            if in_string:
                current.append(char)
                if char == string_char:
                    in_string = False
                    string_char = None
                continue
            
            if char in ('"', "'"):
                in_string = True
                string_char = char
                current.append(char)
                continue
            
            if char == ',':
                parts.append(''.join(current))
                current = []
            else:
                current.append(char)
        
        if current:
            parts.append(''.join(current))
        
        return parts
    
    def _is_valid_css_property(self, value: str) -> bool:
        """Check if the value is a valid CSS property."""
        value = value.strip()
        
        # Allow camelCase or kebab-case properties
        pattern = r'^[a-zA-Z][a-zA-Z0-9-]*$'
        return bool(re.match(pattern, value))
    
    def _is_identifier(self, value: str) -> bool:
        """Check if the value is a valid JavaScript identifier."""
        value = value.strip()
        return bool(re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$', value))