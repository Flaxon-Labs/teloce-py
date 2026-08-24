"""
Interpolation parser for Teloce templates.

Parses {{ expression }} interpolations.
"""

from typing import Optional, List
from teloce.ast.nodes import InterpolationNode
from teloce.template.expressions import ExpressionParser


class InterpolationParser:
    """
    Parses interpolations in Teloce templates.
    """
    
    def __init__(self):
        self.errors: List[str] = []
    
    def parse(self, expression: str) -> Optional[InterpolationNode]:
        """
        Parse an interpolation expression.
        
        Args:
            expression: The expression inside {{ }}
            
        Returns:
            An InterpolationNode or None if parsing fails.
        """
        self.errors = []
        
        if not expression or not expression.strip():
            self.errors.append("Empty interpolation expression")
            return None
        
        # Parse the expression
        expr_parser = ExpressionParser()
        ast = expr_parser.parse(expression)
        
        if expr_parser.errors:
            self.errors.extend(expr_parser.errors)
            return None
        
        # Create interpolation node with the expression
        return InterpolationNode(expression.strip())
    
    def parse_template(self, source: str) -> List[InterpolationNode]:
        """
        Parse all interpolations in a template.
        
        Args:
            source: The template source
            
        Returns:
            A list of InterpolationNode objects.
        """
        self.errors = []
        interpolations = []
        
        # Find all {{ }} patterns
        import re
        pattern = r'\{\{([^}]*)\}\}'
        for match in re.finditer(pattern, source):
            expression = match.group(1).strip()
            if expression:
                node = self.parse(expression)
                if node:
                    interpolations.append(node)
        
        return interpolations
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0