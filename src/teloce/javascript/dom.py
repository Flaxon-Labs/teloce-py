"""
DOM generator - generates DOM operations for templates.
"""

from typing import List, Optional, Dict, Any
import json
from teloce.ast.nodes import (
    ASTNode, ElementNode, TextNode, InterpolationNode,
    ForNode, IfNode, EventNode, BindingNode,
    ComponentNode, SlotNode, FragmentNode
)


class DOMGenerator:
    """
    Generates DOM operations from AST nodes.
    """
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}
        self.minify = self.options.get('minify', False)
        self.dev = self.options.get('dev', True)
        self.indent_level = 0
    
    def generate_element(self, node: ElementNode) -> str:
        """Generate DOM creation for an element."""
        tag = node.tag
        
        lines = ["(() => {", f"  const element = document.createElement('{tag}');"]
        for name, value in node.attributes.items():
            lines.append(f"  element.setAttribute({name!r}, {str(value)!r});")
        for binding in node.bindings:
            lines.append(f"  element.setAttribute({json.dumps(binding.name)}, String({binding.value} ?? ''));" )
        for event in node.events:
            handler = event.handler or '() => {}'
            if handler.isidentifier():
                handler = f"(event) => {handler}(event)"
            elif handler.endswith(')'):
                handler = f"(event) => {{ {handler}; }}"
            lines.append(f"  element.addEventListener({json.dumps(event.name)}, {handler});")
        for child in node.children:
            child_code = self.generate_node(child)
            lines.append(f"  {{ const child = {child_code}; element.appendChild(child); }}")
        lines.extend(["  return element;", "})()"])
        return "\n".join(lines)
    
    def generate_text(self, node: TextNode) -> str:
        """Generate DOM creation for text."""
        return f"document.createTextNode({node.value!r})"
    
    def generate_interpolation(self, node: InterpolationNode) -> str:
        """Generate DOM creation for interpolation."""
        return f"document.createTextNode({node.expression})"
    
    def generate_for(self, node: ForNode) -> str:
        """Generate DOM creation for a for loop."""
        item = node.item or 'item'
        collection = node.collection or 'items'
        key = node.key or 'index'
        key_expression = 'i' if key == 'index' else f'{item}.{key}'
        
        # Generate the loop
        children = []
        for child in node.children:
            children.append(self.generate_node(child))
        
        child_code = children[0] if len(children) == 1 else self.generate_fragment(node.children)
        return f"""(() => {{
  const fragment = document.createDocumentFragment();
  for (let i = 0; i < ({collection} ?? []).length; i++) {{
    const {item} = {collection}[i];
    const {key} = {key_expression};
    fragment.appendChild({child_code});
  }}
  return fragment;
}})()"""
    
    def generate_if(self, node: IfNode) -> str:
        """Generate DOM creation for an if condition."""
        condition = node.condition or 'condition'
        
        children = []
        for child in node.children:
            children.append(self.generate_node(child))
        
        else_children = []
        for child in node.else_children:
            else_children.append(self.generate_node(child))
        
        children_str = self.generate_fragment(node.children)
        else_str = self.generate_fragment(node.else_children)
        return f"(({condition}) ? {children_str} : {else_str})"
    
    def generate_component(self, node: ComponentNode) -> str:
        """Generate DOM creation for a component."""
        name = node.name
        
        # Generate props
        props = []
        for prop_name, prop_value in node.props.items():
            props.append(f"{prop_name}: {prop_value}")
        
        props_str = f"{{{', '.join(props)}}}" if props else "{}"
        
        return f"{name}({props_str})"
    
    def generate_slot(self, node: SlotNode) -> str:
        """Generate DOM creation for a slot."""
        return "document.createTextNode('')"
    
    def generate_fragment(self, node: FragmentNode) -> str:
        """Generate DOM creation for a fragment."""
        children = []
        for child in node.children:
            children.append(self.generate_node(child))
        
        return "(() => { const fragment = document.createDocumentFragment(); " + " ".join(
            f"fragment.appendChild({child});" for child in children
        ) + " return fragment; })()"
    
    def generate_node(self, node: ASTNode) -> str:
        """Generate DOM creation for any node."""
        if isinstance(node, ElementNode):
            return self.generate_element(node)
        elif isinstance(node, TextNode):
            return self.generate_text(node)
        elif isinstance(node, InterpolationNode):
            return self.generate_interpolation(node)
        elif isinstance(node, ForNode):
            return self.generate_for(node)
        elif isinstance(node, IfNode):
            return self.generate_if(node)
        elif isinstance(node, ComponentNode):
            return self.generate_component(node)
        elif isinstance(node, SlotNode):
            return self.generate_slot(node)
        elif isinstance(node, FragmentNode):
            return self.generate_fragment(node)
        else:
            return "document.createTextNode('')"
