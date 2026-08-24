"""
Tests for the AST module.
"""

import pytest

from teloce.ast.nodes import (
    ASTNode, ElementNode, TextNode, InterpolationNode,
    ForNode, IfNode, EventNode, BindingNode,
    ComponentNode, SlotNode, FragmentNode, NodeType
)
from teloce.ast.visitors import ASTVisitor, ASTTransformer, ASTPrinter


class TestAST:
    """Tests for the AST."""

    def test_element_node(self):
        """Test element node creation."""
        node = ElementNode('div', {'class': 'container'}, children=[TextNode('Hello')])
        assert node.tag == 'div'
        assert node.attributes.get('class') == 'container'
        assert len(node.children) == 1
        assert isinstance(node.children[0], TextNode)

    def test_interpolation_node(self):
        """Test interpolation node creation."""
        node = InterpolationNode('message')
        assert node.expression == 'message'

    def test_for_node(self):
        """Test for node creation."""
        node = ForNode('item', 'items', 'id', [TextNode('Hello')])
        assert node.item == 'item'
        assert node.collection == 'items'
        assert node.key == 'id'
        assert len(node.children) == 1

    def test_if_node(self):
        """Test if node creation."""
        node = IfNode('isVisible', [TextNode('Visible')], [TextNode('Hidden')])
        assert node.condition == 'isVisible'
        assert len(node.children) == 1
        assert len(node.else_children) == 1

    def test_event_node(self):
        """Test event node creation."""
        node = EventNode('click', 'handleClick')
        assert node.name == 'click'
        assert node.handler == 'handleClick'

    def test_binding_node(self):
        """Test binding node creation."""
        node = BindingNode('class', 'className')
        assert node.name == 'class'
        assert node.value == 'className'

    def test_component_node(self):
        """Test component node creation."""
        node = ComponentNode('MyComponent', {'prop': 'value'}, [TextNode('Child')])
        assert node.name == 'MyComponent'
        assert node.props.get('prop') == 'value'
        assert len(node.children) == 1

    def test_slot_node(self):
        """Test slot node creation."""
        node = SlotNode('header', [TextNode('Content')])
        assert node.name == 'header'
        assert len(node.children) == 1

    def test_fragment_node(self):
        """Test fragment node creation."""
        node = FragmentNode([TextNode('Hello'), TextNode('World')])
        assert len(node.children) == 2

    def test_visitor(self):
        """Test AST visitor."""
        class TestVisitor(ASTVisitor):
            def __init__(self):
                self.visited = []
            
            def visit_element(self, node):
                self.visited.append('element')
            
            def visit_text(self, node):
                self.visited.append('text')
        
        visitor = TestVisitor()
        node = ElementNode('div', children=[TextNode('Hello')])
        visitor.visit(node)
        assert 'element' in visitor.visited
        assert 'text' in visitor.visited

    def test_transformer(self):
        """Test AST transformer."""
        class TestTransformer(ASTTransformer):
            def visit_text(self, node):
                return TextNode('Transformed')
        
        transformer = TestTransformer()
        node = ElementNode('div', children=[TextNode('Original')])
        result = transformer.visit(node)
        assert isinstance(result, ElementNode)
        assert result.children[0].value == 'Transformed'