"""
Optimizer for the AST.

Applies optimization passes to the AST for better performance.
"""

from typing import List, Optional, Any, Set

from teloce.ast.nodes import (
    ASTNode, ElementNode, TextNode, InterpolationNode, ForNode, IfNode,
    ComponentNode, SlotNode, FragmentNode,
)


class Optimizer:
    """
    Optimizes the AST for better performance.
    """
    
    def __init__(self, options: Optional[dict] = None):
        self.options = options or {}
        self.static_nodes: Set[int] = set()
    
    def optimize(self, nodes: List[ASTNode]) -> List[ASTNode]:
        """Optimize the AST."""
        # First pass: mark static nodes
        self._mark_static_nodes(nodes)
        
        # Second pass: optimize
        return self._optimize_nodes(nodes)
    
    def _mark_static_nodes(self, nodes: List[ASTNode]):
        """Mark static nodes that don't need reactivity."""
        for node in nodes:
            self._mark_static_node(node)
    
    def _mark_static_node(self, node: ASTNode):
        """Mark a single node as static or dynamic."""
        if isinstance(node, InterpolationNode):
            # Interpolations are dynamic
            return
        
        if isinstance(node, ElementNode):
            # Check for dynamic attributes
            has_dynamic = False
            
            # Events are dynamic
            if node.events:
                has_dynamic = True
            
            # Bindings are dynamic
            if node.bindings:
                has_dynamic = True
            
            # A parent is dynamic when any descendant is dynamic.
            child_static = all(self._mark_static_node(child) for child in node.children)
            if not has_dynamic and child_static:
                # If no dynamic content, it's static
                self.static_nodes.add(id(node))
                return True
            return False
        if isinstance(node, (ForNode, IfNode, ComponentNode, SlotNode, FragmentNode)):
            children = list(getattr(node, 'children', []))
            if isinstance(node, IfNode):
                children += node.else_children
            return all(self._mark_static_node(child) for child in children)
        return True
    
    def _optimize_nodes(self, nodes: List[ASTNode]) -> List[ASTNode]:
        """Optimize a list of nodes."""
        result = []
        for node in nodes:
            optimized = self._optimize_node(node)
            if optimized:
                if isinstance(optimized, TextNode) and result and isinstance(result[-1], TextNode):
                    result[-1] = TextNode(
                        result[-1].value + optimized.value,
                        result[-1].line,
                        result[-1].column,
                    )
                else:
                    result.append(optimized)
        return result
    
    def _optimize_node(self, node: ASTNode) -> Optional[ASTNode]:
        """Optimize a single node."""
        if isinstance(node, ElementNode):
            return self._optimize_element(node)
        if isinstance(node, ForNode):
            node.children = self._optimize_nodes(node.children)
        elif isinstance(node, IfNode):
            node.children = self._optimize_nodes(node.children)
            node.else_children = self._optimize_nodes(node.else_children)
        elif isinstance(node, (ComponentNode, SlotNode, FragmentNode)):
            node.children = self._optimize_nodes(node.children)
        return node
    
    def _optimize_element(self, node: ElementNode) -> ElementNode:
        """Optimize an element node."""
        # Optimize children
        optimized_children = []
        for child in node.children:
            optimized = self._optimize_node(child)
            if optimized:
                optimized_children.append(optimized)
        
        return ElementNode(
            node.tag,
            node.attributes,
            node.events,
            node.bindings,
            optimized_children,
            node.line,
            node.column
        )
