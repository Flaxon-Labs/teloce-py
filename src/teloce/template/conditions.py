"""
Condition parser for Teloce templates.

Parses <if>, <else if>, and <else> directives.
"""

from typing import Optional, List, Dict, Any
from teloce.ast.nodes import IfNode, ElseNode


class ConditionParser:
    """
    Parses conditional directives.
    """
    
    def __init__(self):
        self.errors: List[str] = []
    
    def parse_if(self, condition: str, children: List,
                 else_children: List = None) -> Optional[IfNode]:
        """
        Parse an if directive.
        
        Args:
            condition: The condition expression
            children: The child nodes of the if tag
            else_children: The child nodes of the else branch
            
        Returns:
            An IfNode or None if parsing fails.
        """
        self.errors = []
        
        if not condition or not condition.strip():
            self.errors.append("Missing condition in if directive")
            return None
        
        return IfNode(condition, children or [], else_children or [])
    
    def parse_else(self, children: List) -> Optional[ElseNode]:
        """
        Parse an else directive.
        
        Args:
            children: The child nodes of the else tag
            
        Returns:
            An ElseNode or None if parsing fails.
        """
        self.errors = []
        
        return ElseNode(children or [])
    
    def parse_else_if(self, condition: str, children: List) -> Optional[IfNode]:
        """
        Parse an else-if directive.
        
        Args:
            condition: The condition expression
            children: The child nodes
            
        Returns:
            An IfNode or None if parsing fails.
        """
        self.errors = []
        
        if not condition or not condition.strip():
            self.errors.append("Missing condition in else-if directive")
            return None
        
        return IfNode(condition, children or [])
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0