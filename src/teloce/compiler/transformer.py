"""
Transformer for optimizing the AST.

Applies transformations to the AST for optimization.
"""

from typing import List, Optional, Any

from teloce.ast.nodes import ASTNode, ElementNode, TextNode, InterpolationNode


class Transformer:
    """
    Transforms the AST for optimization.
    """
    
    def __init__(self):
        self.errors: List[str] = []
    
    def transform(self, nodes: List[ASTNode]) -> List[ASTNode]:
        """Transform the AST."""
        self.errors = []
        return self._transform_nodes(nodes)
    
    def _transform_nodes(self, nodes: List[ASTNode]) -> List[ASTNode]:
        """Transform a list of nodes."""
        result = []
        for node in nodes:
            transformed = self._transform_node(node)
            if transformed:
                result.append(transformed)
        return result
    
    def _transform_node(self, node: ASTNode) -> Optional[ASTNode]:
        """Transform a single node."""
        if isinstance(node, ElementNode):
            return self._transform_element(node)
        elif isinstance(node, InterpolationNode):
            return self._transform_interpolation(node)
        elif isinstance(node, TextNode):
            return node
        else:
            return node
    
    def _transform_element(self, node: ElementNode) -> ElementNode:
        """Transform an element node."""
        # Transform children
        transformed_children = []
        for child in node.children:
            transformed = self._transform_node(child)
            if transformed:
                transformed_children.append(transformed)
        
        return ElementNode(
            node.tag,
            node.attributes,
            node.events,
            node.bindings,
            transformed_children,
            node.line,
            node.column
        )
    
    def _transform_interpolation(self, node: InterpolationNode) -> InterpolationNode:
        """Transform an interpolation node."""
        # Could optimize expressions here
        return node
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
