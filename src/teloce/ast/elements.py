"""
Element factory and utilities.

Provides utilities for creating and working with element nodes.
"""

from typing import List, Optional, Set

from teloce.ast.nodes import ElementNode


# HTML void elements (self-closing)
VOID_ELEMENTS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr',
    'command', 'keygen', 'menuitem'
}

# Container elements (can have children)
CONTAINER_ELEMENTS = {
    'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'a', 'button', 'form', 'input', 'label', 'select', 'textarea',
    'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'thead', 'tbody',
    'section', 'article', 'header', 'footer', 'nav', 'main', 'aside',
    'figure', 'figcaption', 'blockquote', 'pre', 'code', 'em', 'strong',
    'i', 'b', 'u', 's', 'small', 'mark', 'del', 'ins', 'sub', 'sup',
    'iframe', 'video', 'audio', 'canvas', 'svg', 'template'
}


class ElementFactory:
    """
    Factory for creating element nodes.
    """
    
    @staticmethod
    def is_void(tag: str) -> bool:
        """Check if a tag is a void element."""
        return tag.lower() in VOID_ELEMENTS
    
    @staticmethod
    def is_container(tag: str) -> bool:
        """Check if a tag is a container element."""
        return tag.lower() in CONTAINER_ELEMENTS or tag.lower() not in VOID_ELEMENTS
    
    @staticmethod
    def create(tag: str, attributes: dict = None,
               children: List = None, line: int = 0, column: int = 0) -> ElementNode:
        """Create an element node."""
        return ElementNode(tag, attributes, children=children or [], line=line, column=column)
    
    @staticmethod
    def create_void(tag: str, attributes: dict = None,
                    line: int = 0, column: int = 0) -> ElementNode:
        """Create a void (self-closing) element."""
        return ElementNode(tag, attributes, children=[], line=line, column=column)


class VoidElement:
    """
    Represents a void (self-closing) HTML element.
    """
    
    @staticmethod
    def is_void(tag: str) -> bool:
        return tag.lower() in VOID_ELEMENTS
    
    @staticmethod
    def get_all() -> Set[str]:
        return VOID_ELEMENTS.copy()


class ContainerElement:
    """
    Represents a container HTML element that can have children.
    """
    
    @staticmethod
    def is_container(tag: str) -> bool:
        return tag.lower() in CONTAINER_ELEMENTS or tag.lower() not in VOID_ELEMENTS
    
    @staticmethod
    def get_all() -> Set[str]:
        return CONTAINER_ELEMENTS.copy()
