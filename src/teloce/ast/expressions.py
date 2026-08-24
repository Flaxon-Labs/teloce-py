"""
Expression AST nodes.

Defines AST nodes for expressions used in templates.
"""

from dataclasses import dataclass
from typing import List, Optional, Any
from enum import Enum, auto


class ExpressionType(Enum):
    """Types of expression nodes."""
    IDENTIFIER = auto()
    LITERAL = auto()
    BINARY = auto()
    UNARY = auto()
    CALL = auto()
    MEMBER = auto()
    ARRAY = auto()
    OBJECT = auto()


@dataclass
class ExpressionNode:
    """Base class for expression nodes."""
    type: ExpressionType
    line: int = 0
    column: int = 0


@dataclass(init=False)
class IdentifierNode(ExpressionNode):
    """Identifier expression node."""
    name: str
    
    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(ExpressionType.IDENTIFIER, line, column)
        self.name = name
    
    def __repr__(self) -> str:
        return f"Identifier({self.name})"


@dataclass(init=False)
class LiteralNode(ExpressionNode):
    """Literal value expression node."""
    value: Any
    
    def __init__(self, value: Any, line: int = 0, column: int = 0):
        super().__init__(ExpressionType.LITERAL, line, column)
        self.value = value
    
    def __repr__(self) -> str:
        return f"Literal({repr(self.value)})"


@dataclass(init=False)
class BinaryNode(ExpressionNode):
    """Binary operation expression node."""
    left: ExpressionNode
    operator: str
    right: ExpressionNode
    
    def __init__(self, left: ExpressionNode, operator: str,
                 right: ExpressionNode, line: int = 0, column: int = 0):
        super().__init__(ExpressionType.BINARY, line, column)
        self.left = left
        self.operator = operator
        self.right = right
    
    def __repr__(self) -> str:
        return f"Binary({self.left} {self.operator} {self.right})"


@dataclass(init=False)
class UnaryNode(ExpressionNode):
    """Unary operation expression node."""
    operator: str
    operand: ExpressionNode
    
    def __init__(self, operator: str, operand: ExpressionNode,
                 line: int = 0, column: int = 0):
        super().__init__(ExpressionType.UNARY, line, column)
        self.operator = operator
        self.operand = operand
    
    def __repr__(self) -> str:
        return f"Unary({self.operator}{self.operand})"


@dataclass(init=False)
class CallNode(ExpressionNode):
    """Function call expression node."""
    callee: ExpressionNode
    arguments: List[ExpressionNode]
    
    def __init__(self, callee: ExpressionNode, arguments: List[ExpressionNode] = None,
                 line: int = 0, column: int = 0):
        super().__init__(ExpressionType.CALL, line, column)
        self.callee = callee
        self.arguments = arguments or []
    
    def __repr__(self) -> str:
        return f"Call({self.callee}, {self.arguments})"


@dataclass(init=False)
class MemberNode(ExpressionNode):
    """Member access expression node."""
    object: ExpressionNode
    property: str
    computed: bool = False
    
    def __init__(self, object: ExpressionNode, property: str,
                 computed: bool = False, line: int = 0, column: int = 0):
        super().__init__(ExpressionType.MEMBER, line, column)
        self.object = object
        self.property = property
        self.computed = computed
    
    def __repr__(self) -> str:
        return f"Member({self.object}.{self.property})"


@dataclass(init=False)
class ArrayNode(ExpressionNode):
    """Array literal expression node."""
    elements: List[ExpressionNode]
    
    def __init__(self, elements: List[ExpressionNode] = None,
                 line: int = 0, column: int = 0):
        super().__init__(ExpressionType.ARRAY, line, column)
        self.elements = elements or []
    
    def __repr__(self) -> str:
        return f"Array({self.elements})"


@dataclass(init=False)
class ObjectNode(ExpressionNode):
    """Object literal expression node."""
    properties: List[tuple]
    
    def __init__(self, properties: List[tuple] = None,
                 line: int = 0, column: int = 0):
        super().__init__(ExpressionType.OBJECT, line, column)
        self.properties = properties or []
    
    def __repr__(self) -> str:
        return f"Object({self.properties})"
