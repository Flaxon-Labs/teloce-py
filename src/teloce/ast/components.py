"""
Component AST nodes.

Defines nodes for custom components and component-related structures.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from teloce.ast.nodes import ASTNode, NodeType


@dataclass(init=False)
class ComponentReference(ASTNode):
    """
    Reference to a custom component.
    """
    name: str
    props: Dict[str, str] = field(default_factory=dict)
    children: List[ASTNode] = field(default_factory=list)
    slots: Dict[str, List[ASTNode]] = field(default_factory=dict)
    
    def __init__(self, name: str, props: Dict[str, str] = None,
                 children: List[ASTNode] = None,
                 slots: Dict[str, List[ASTNode]] = None,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.COMPONENT, line, column)
        self.name = name
        self.props = props or {}
        self.children = children or []
        self.slots = slots or {}
    
    def accept(self, visitor):
        return visitor.visit_component(self)


@dataclass(init=False)
class ComponentSlot(ASTNode):
    """
    Slot definition inside a component.
    """
    name: str = "default"
    fallback: List[ASTNode] = field(default_factory=list)
    
    def __init__(self, name: str = "default", fallback: List[ASTNode] = None,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.SLOT, line, column)
        self.name = name
        self.fallback = fallback or []
    
    def accept(self, visitor):
        return visitor.visit_slot(self)


@dataclass(init=False)
class ComponentProp(ASTNode):
    """
    Prop definition for a component.
    """
    name: str
    type: Optional[str] = None
    required: bool = False
    default: Any = None
    validator: Optional[str] = None
    
    def __init__(self, name: str, type: str = None, required: bool = False,
                 default: Any = None, validator: str = None,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.ATTRIBUTE, line, column)
        self.name = name
        self.type = type
        self.required = required
        self.default = default
        self.validator = validator
    
    def accept(self, visitor):
        return visitor.visit_attribute(self)
