"""
CSS Generator - generates CSS from component styles.

Handles scoped CSS generation and minification.
"""

from typing import Optional, Dict, Any, List
import re

from teloce.css.parser import CSSParser, CSSStylesheet, CSSRule, CSSAtRule, CSSDeclaration
from teloce.css.scoped import CSSScoper
from teloce.css.hashing import HashGenerator
from teloce.css.modules import CSSModules


class CSSGenerator:
    """
    Generates CSS from component styles.
    """
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}
        self.minify = self.options.get('minify', False)
        self.scoped = self.options.get('scoped', True)
        self.hash_gen = HashGenerator()
        self.scoper = CSSScoper()
    
    def generate(self, css: str, component_name: str = "Component") -> str:
        """
        Generate CSS from the component styles.
        
        Args:
            css: The raw CSS source
            component_name: The component name
            
        Returns:
            Generated CSS.
        """
        if not css or not css.strip():
            return ""

        if self.options.get("module", False):
            css, _ = CSSModules.transform_css(css, component_name)
        
        # Parse the CSS
        parser = CSSParser()
        stylesheet = parser.parse(css)
        
        if parser.errors:
            # Return raw CSS if parsing fails
            return css
        
        # Generate CSS
        generated = self._generate_from_stylesheet(stylesheet, component_name)
        
        # Minify if requested
        if self.minify:
            generated = self._minify(generated)
        
        return generated
    
    def _generate_from_stylesheet(self, stylesheet: CSSStylesheet, component_name: str) -> str:
        """Generate CSS from a stylesheet AST."""
        if not stylesheet.rules and not stylesheet.at_rules:
            return ""
        
        # If scoped, scope the CSS
        if self.scoped:
            scope_id = self.hash_gen.generate_scope_id(component_name)
            return self.scoper.scope(self._to_css(stylesheet), scope_id)
        
        return self._to_css(stylesheet)
    
    def _to_css(self, stylesheet: CSSStylesheet) -> str:
        """Convert a stylesheet to CSS string."""
        parts = []
        
        for rule in stylesheet.rules:
            parts.append(self._rule_to_css(rule))
        
        for at_rule in stylesheet.at_rules:
            parts.append(self._at_rule_to_css(at_rule))
        
        return '\n'.join(parts)
    
    def _rule_to_css(self, rule: CSSRule) -> str:
        """Convert a rule to CSS string."""
        if not rule.declarations:
            return ""
        
        declarations = []
        for decl in rule.declarations:
            declarations.append(f"{decl.property}: {decl.value}")
        
        return f"{rule.selector} {{ {'; '.join(declarations)} }}"
    
    def _at_rule_to_css(self, at_rule: CSSAtRule) -> str:
        """Convert an at-rule to CSS string."""
        if at_rule.rules:
            rules = []
            for rule in at_rule.rules:
                rules.append(self._rule_to_css(rule))
            return f"@{at_rule.name} {at_rule.value} {{ {' '.join(rules)} }}"
        
        if at_rule.declarations:
            declarations = []
            for decl in at_rule.declarations:
                declarations.append(f"{decl.property}: {decl.value}")
            return f"@{at_rule.name} {at_rule.value} {{ {'; '.join(declarations)} }}"
        
        return f"@{at_rule.name} {at_rule.value};"
    
    def _minify(self, css: str) -> str:
        """Minify CSS."""
        # Remove comments
        css = re.sub(r'/\*[\s\S]*?\*/', '', css)
        
        # Remove whitespace
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r'{\s+', '{', css)
        css = re.sub(r'\s+}', '}', css)
        css = re.sub(r':\s+', ':', css)
        css = re.sub(r';\s+', ';', css)
        css = re.sub(r',\s+', ',', css)
        
        # Remove trailing semicolons
        css = re.sub(r';}', '}', css)
        
        return css.strip()
    
    def generate_scoped_css(self, css: str, component_name: str) -> str:
        """
        Generate scoped CSS for a component.
        
        Args:
            css: The raw CSS source
            component_name: The component name
            
        Returns:
            Scoped CSS.
        """
        scope_id = self.hash_gen.generate_scope_id(component_name)
        return self.scoper.scope(css, scope_id)
    
    def generate_style_tag(self, css: str, component_name: str = "Component") -> str:
        """
        Generate a style tag with scoped CSS.
        
        Args:
            css: The raw CSS source
            component_name: The component name
            
        Returns:
            A style tag HTML string.
        """
        scoped_css = self.generate_scoped_css(css, component_name)
        if not scoped_css:
            return ""
        
        return f"<style scoped>\n{scoped_css}\n</style>"
