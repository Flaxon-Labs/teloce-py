"""
AST visitors for traversing and transforming the AST.

Provides visitor patterns for AST traversal and transformation.
"""

from typing import List, Optional, Any, Callable
from teloce.ast.nodes import (
    ASTNode, NodeType,
    ElementNode, TextNode, InterpolationNode,
    ForNode, IfNode, ElseNode, EventNode, BindingNode,
    ComponentNode, SlotNode, FragmentNode,
    AttributeNode, CommentNode, DoctypeNode
)


class ASTVisitor:
    """
    Base visitor for AST traversal.
    
    Subclass this and override visit_* methods for specific node types.
    """
    
    def visit(self, node: ASTNode) -> Any:
        """Visit a node."""
        method_name = f"visit_{node.type.name.lower()}"
        method = getattr(self, method_name, None)
        if method:
            result = method(node)
            # A small visitor override should not accidentally stop traversal.
            # The built-in methods already recurse, so only recurse here when
            # the concrete visitor replaced one of those methods.
            base_method = getattr(ASTVisitor, method_name, None)
            if method_name == "visit_element" and getattr(method, "__func__", method) is not base_method:
                for child in node.children:
                    self.visit(child)
            return result
        return self.visit_default(node)
    
    def visit_default(self, node: ASTNode) -> Any:
        """Default visit method."""
        return None
    
    def visit_element(self, node: ElementNode) -> Any:
        """Visit an element node."""
        for child in node.children:
            self.visit(child)
        return None
    
    def visit_text(self, node: TextNode) -> Any:
        """Visit a text node."""
        return None
    
    def visit_interpolation(self, node: InterpolationNode) -> Any:
        """Visit an interpolation node."""
        return None
    
    def visit_for(self, node: ForNode) -> Any:
        """Visit a for node."""
        for child in node.children:
            self.visit(child)
        return None
    
    def visit_if(self, node: IfNode) -> Any:
        """Visit an if node."""
        for child in node.children:
            self.visit(child)
        for child in node.else_children:
            self.visit(child)
        return None
    
    def visit_else(self, node: ElseNode) -> Any:
        """Visit an else node."""
        for child in node.children:
            self.visit(child)
        return None
    
    def visit_event(self, node: EventNode) -> Any:
        """Visit an event node."""
        return None
    
    def visit_binding(self, node: BindingNode) -> Any:
        """Visit a binding node."""
        return None
    
    def visit_component(self, node: ComponentNode) -> Any:
        """Visit a component node."""
        for child in node.children:
            self.visit(child)
        for slot_children in node.slots.values():
            for child in slot_children:
                self.visit(child)
        return None
    
    def visit_slot(self, node: SlotNode) -> Any:
        """Visit a slot node."""
        for child in node.children:
            self.visit(child)
        return None
    
    def visit_fragment(self, node: FragmentNode) -> Any:
        """Visit a fragment node."""
        for child in node.children:
            self.visit(child)
        return None
    
    def visit_attribute(self, node: AttributeNode) -> Any:
        """Visit an attribute node."""
        return None
    
    def visit_comment(self, node: CommentNode) -> Any:
        """Visit a comment node."""
        return None
    
    def visit_doctype(self, node: DoctypeNode) -> Any:
        """Visit a doctype node."""
        return None


class ASTTransformer(ASTVisitor):
    """
    AST transformer that can modify nodes.
    
    Override visit_* methods to transform specific node types.
    """
    
    def visit(self, node: ASTNode) -> ASTNode:
        """Visit and possibly transform a node."""
        method_name = f"visit_{node.type.name.lower()}"
        method = getattr(self, method_name, None)
        if method:
            return method(node)
        return self.visit_default(node)
    
    def visit_default(self, node: ASTNode) -> ASTNode:
        """Default visit method returns the node unchanged."""
        return node
    
    def visit_element(self, node: ElementNode) -> ASTNode:
        """Transform an element node."""
        transformed_children = []
        for child in node.children:
            transformed = self.visit(child)
            if transformed:
                transformed_children.append(transformed)
        
        node.children = transformed_children
        return node
    
    def visit_for(self, node: ForNode) -> ASTNode:
        """Transform a for node."""
        transformed_children = []
        for child in node.children:
            transformed = self.visit(child)
            if transformed:
                transformed_children.append(transformed)
        
        node.children = transformed_children
        return node
    
    def visit_if(self, node: IfNode) -> ASTNode:
        """Transform an if node."""
        transformed_children = []
        for child in node.children:
            transformed = self.visit(child)
            if transformed:
                transformed_children.append(transformed)
        
        transformed_else = []
        for child in node.else_children:
            transformed = self.visit(child)
            if transformed:
                transformed_else.append(transformed)
        
        node.children = transformed_children
        node.else_children = transformed_else
        return node


class ASTPrinter(ASTVisitor):
    """
    Pretty printer for AST nodes.
    
    Prints the AST in a human-readable format.
    """
    
    def __init__(self):
        self.indent_level = 0
    
    def _indent(self) -> str:
        return "  " * self.indent_level
    
    def _print(self, message: str):
        print(f"{self._indent()}{message}")
    
    def visit_default(self, node: ASTNode) -> Any:
        self._print(f"{node.type.name}:")
        return None
    
    def visit_element(self, node: ElementNode) -> Any:
        self._print(f"Element: {node.tag}")
        if node.attributes:
            self.indent_level += 1
            for name, value in node.attributes.items():
                self._print(f"Attr: {name}=\"{value}\"")
            self.indent_level -= 1
        if node.children:
            self.indent_level += 1
            for child in node.children:
                self.visit(child)
            self.indent_level -= 1
        return None
    
    def visit_text(self, node: TextNode) -> Any:
        self._print(f"Text: \"{node.value[:50]}\"")
        return None
    
    def visit_interpolation(self, node: InterpolationNode) -> Any:
        self._print(f"Interpolation: {node.expression}")
        return None
    
    def visit_for(self, node: ForNode) -> Any:
        self._print(f"For: {node.item} in {node.collection}")
        if node.key:
            self._print(f"  Key: {node.key}")
        if node.children:
            self.indent_level += 1
            for child in node.children:
                self.visit(child)
            self.indent_level -= 1
        return None
    
    def visit_if(self, node: IfNode) -> Any:
        self._print(f"If: {node.condition}")
        if node.children:
            self.indent_level += 1
            for child in node.children:
                self.visit(child)
            self.indent_level -= 1
        if node.else_children:
            self._print("Else:")
            self.indent_level += 1
            for child in node.else_children:
                self.visit(child)
            self.indent_level -= 1
        return None
