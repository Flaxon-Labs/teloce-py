"""
Style parser for .vel components.

Parses the <style> section of a .vel file with full CSS parsing,
validation, and scoping support.
"""

import re
import hashlib
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field

from teloce.sfc.component import ComponentStyle


@dataclass
class CSSRule:
    """Represents a CSS rule."""
    selector: str
    declarations: Dict[str, str]
    line: int = 0
    column: int = 0


@dataclass
class CSSAtRule:
    """Represents a CSS at-rule (@media, @keyframes, etc.)."""
    name: str
    value: str
    rules: List[CSSRule] = field(default_factory=list)
    line: int = 0
    column: int = 0


@dataclass
class CSSStylesheet:
    """Represents a complete CSS stylesheet."""
    rules: List[CSSRule] = field(default_factory=list)
    at_rules: List[CSSAtRule] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)


class CSSParser:
    """
    Parses CSS stylesheets.
    """
    
    def __init__(self):
        self.errors: List[str] = []
        self.position = 0
        self.source = ""
        self.line = 1
        self.column = 1
    
    def parse(self, source: str) -> CSSStylesheet:
        """Parse a CSS stylesheet."""
        self.errors = []
        self.position = 0
        self.source = source
        self.line = 1
        self.column = 1
        
        stylesheet = CSSStylesheet()
        
        while self.position < len(self.source):
            self._skip_whitespace_and_comments()
            
            if self.position >= len(self.source):
                break
            
            # Check for at-rule
            if self._peek() == '@':
                at_rule = self._parse_at_rule()
                if at_rule:
                    stylesheet.at_rules.append(at_rule)
            else:
                rule = self._parse_rule()
                if rule:
                    stylesheet.rules.append(rule)
        
        return stylesheet
    
    def _parse_rule(self) -> Optional[CSSRule]:
        """Parse a CSS rule."""
        start_line = self.line
        start_col = self.column
        
        # Read selector
        selector = self._read_selector()
        if not selector:
            return None
        
        self._skip_whitespace_and_comments()
        
        if self._peek() != '{':
            self.errors.append(f"Expected '{{' at line {self.line}")
            return None
        
        self._advance()  # Skip '{'
        
        # Parse declarations
        declarations = {}
        
        while self.position < len(self.source):
            self._skip_whitespace_and_comments()
            
            if self._peek() == '}':
                self._advance()  # Skip '}'
                break
            
            # Read property
            prop = self._read_property()
            if not prop:
                self._advance()
                continue
            
            self._skip_whitespace_and_comments()
            
            if self._peek() != ':':
                self.errors.append(f"Expected ':' at line {self.line}")
                continue
            
            self._advance()  # Skip ':'
            
            self._skip_whitespace_and_comments()
            
            # Read value
            value = self._read_value()
            if value is not None:
                declarations[prop] = value
            
            self._skip_whitespace_and_comments()
            
            if self._peek() == ';':
                self._advance()  # Skip ';'
        
        return CSSRule(selector.strip(), declarations, start_line, start_col)
    
    def _parse_at_rule(self) -> Optional[CSSAtRule]:
        """Parse a CSS at-rule."""
        start_line = self.line
        start_col = self.column
        
        self._advance()  # Skip '@'
        
        # Read rule name
        name = self._read_identifier()
        if not name:
            return None
        
        self._skip_whitespace_and_comments()
        
        # Read value until '{'
        value = ""
        while self.position < len(self.source):
            if self._peek() == '{':
                break
            value += self._peek()
            self._advance()
        
        value = value.strip()
        
        if self._peek() == '{':
            self._advance()  # Skip '{'
            
            # Parse nested rules
            rules = []
            while self.position < len(self.source):
                self._skip_whitespace_and_comments()
                
                if self._peek() == '}':
                    self._advance()  # Skip '}'
                    break
                
                rule = self._parse_rule()
                if rule:
                    rules.append(rule)
            
            return CSSAtRule(name, value, rules, start_line, start_col)
        
        return CSSAtRule(name, value, [], start_line, start_col)
    
    def _read_selector(self) -> str:
        """Read a CSS selector."""
        start = self.position
        
        while self.position < len(self.source):
            char = self._peek()
            if char == '{':
                break
            self._advance()
        
        return self.source[start:self.position].strip()
    
    def _read_property(self) -> Optional[str]:
        """Read a CSS property name."""
        start = self.position
        
        while self.position < len(self.source):
            char = self._peek()
            if char == ':' or char == ';' or char == '}':
                break
            self._advance()
        
        prop = self.source[start:self.position].strip()
        return prop if prop else None
    
    def _read_value(self) -> Optional[str]:
        """Read a CSS value."""
        start = self.position
        open_parens = 0
        in_quotes = False
        quote_char = None
        
        while self.position < len(self.source):
            char = self._peek()
            
            # Handle quotes
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
            elif in_quotes and char == quote_char:
                in_quotes = False
            elif not in_quotes:
                if char == ';':
                    break
                if char == '}':
                    break
            
            self._advance()
        
        value = self.source[start:self.position].strip()
        return value if value else None
    
    def _read_identifier(self) -> str:
        """Read an identifier."""
        start = self.position
        
        while self.position < len(self.source):
            char = self._peek()
            if not (char.isalnum() or char in '-_'):
                break
            self._advance()
        
        return self.source[start:self.position]
    
    def _skip_whitespace_and_comments(self):
        """Skip whitespace and comments."""
        while self.position < len(self.source):
            char = self._peek()
            
            if char.isspace():
                self._advance()
                continue
            
            # Skip comments
            if char == '/' and self._peek_next() == '*':
                self._advance()  # Skip '/'
                self._advance()  # Skip '*'
                while self.position < len(self.source):
                    if self._peek() == '*' and self._peek_next() == '/':
                        self._advance()  # Skip '*'
                        self._advance()  # Skip '/'
                        break
                    self._advance()
                continue
            
            break
    
    def _peek(self) -> str:
        """Peek at the current character."""
        if self.position >= len(self.source):
            return ''
        return self.source[self.position]
    
    def _peek_next(self) -> str:
        """Peek at the next character."""
        if self.position + 1 >= len(self.source):
            return ''
        return self.source[self.position + 1]
    
    def _advance(self):
        """Advance to the next character."""
        if self.position < len(self.source):
            char = self.source[self.position]
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1


class CSSScoper:
    """
    Scopes CSS selectors with a unique component hash.
    """
    
    def __init__(self):
        self.errors: List[str] = []
    
    def scope(self, css: str, component_name: str, scope_id: str = None) -> str:
        """
        Scope CSS with a unique component ID.
        
        Args:
            css: The CSS source
            component_name: The component name
            scope_id: Optional custom scope ID
            
        Returns:
            Scoped CSS
        """
        self.errors = []
        
        if not css or not css.strip():
            return ""
        
        if not scope_id:
            scope_id = self._generate_scope_id(component_name)
        
        # Parse the CSS
        parser = CSSParser()
        stylesheet = parser.parse(css)
        
        if parser.errors:
            self.errors.extend(parser.errors)
            return css
        
        # Scoped the rules
        scoped_rules = []
        
        for rule in stylesheet.rules:
            scoped_selector = self._scope_selector(rule.selector, scope_id)
            if scoped_selector:
                declarations = ';\n  '.join(f"{k}: {v}" for k, v in rule.declarations.items())
                scoped_rules.append(f"{scoped_selector} {{\n  {declarations}\n}}")
        
        for at_rule in stylesheet.at_rules:
            # Scoped nested rules
            scoped_nested = []
            for rule in at_rule.rules:
                scoped_selector = self._scope_selector(rule.selector, scope_id)
                if scoped_selector:
                    declarations = ';\n  '.join(f"{k}: {v}" for k, v in rule.declarations.items())
                    scoped_nested.append(f"  {scoped_selector} {{\n    {declarations}\n  }}")
            
            if scoped_nested:
                scoped_rules.append(
                    f"@{at_rule.name} {at_rule.value} {{\n" +
                    "\n".join(scoped_nested) +
                    "\n}"
                )
            else:
                scoped_rules.append(f"@{at_rule.name} {at_rule.value} {{}}")
        
        return "\n\n".join(scoped_rules)
    
    def _scope_selector(self, selector: str, scope_id: str) -> str:
        """
        Scope a single CSS selector.
        
        Adds the scope attribute to all selectors.
        """
        # Split selectors by comma (multiple selectors)
        parts = selector.split(',')
        scoped_parts = []
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            scoped_parts.append(self._scope_selector_part(part, scope_id))
        
        return ', '.join(scoped_parts)
    
    def _scope_selector_part(self, selector: str, scope_id: str) -> str:
        """Scope a single selector part."""
        # Handle complex selectors with combinators
        # Split by combinators: >, +, ~, space
        import re
        
        # Tokenize the selector
        tokens = []
        current = ""
        i = 0
        
        while i < len(selector):
            char = selector[i]
            
            # Check for combinators
            if char in '>+~':
                if current:
                    tokens.append(('selector', current.strip()))
                    current = ""
                tokens.append(('combinator', char))
                i += 1
                continue
            
            if char == ' ':
                if current:
                    tokens.append(('selector', current.strip()))
                    current = ""
                # Multiple spaces are combinators
                tokens.append(('combinator', ' '))
                i += 1
                continue
            
            current += char
            i += 1
        
        if current:
            tokens.append(('selector', current.strip()))
        
        # Process tokens
        result = ""
        for token_type, token_value in tokens:
            if token_type == 'selector':
                # Scope the selector
                scoped = self._scope_simple_selector(token_value, scope_id)
                result += scoped
            else:
                result += token_value
        
        return result
    
    def _scope_simple_selector(self, selector: str, scope_id: str) -> str:
        """Scope a simple selector (no combinators)."""
        if not selector:
            return selector
        
        # Handle pseudo-classes
        pseudo_match = re.match(r'^([^:]+)(:.*)?$', selector)
        if pseudo_match:
            base = pseudo_match.group(1)
            pseudo = pseudo_match.group(2) or ""
            
            if base:
                # Add scope attribute to the element
                if base == ':root':
                    return f":root{scope_id}"
                elif base == ':host':
                    return f":host{scope_id}"
                else:
                    return f"{base}{scope_id}{pseudo}"
            else:
                return f"{scope_id}{pseudo}"
        
        # Handle animation keyframes
        if selector.startswith('@keyframes'):
            return selector
        
        # Add scope attribute to the selector
        # If selector is a tag, add attribute
        # If selector is a class or id, add attribute to the element
        # If selector is empty, use attribute only
        
        if not selector or selector == '':
            return f"[{scope_id}]"
        
        # Check if selector is a tag with no class or id
        if re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', selector):
            return f"{selector}[{scope_id}]"
        
        # Add attribute to the base element
        # Find the base element (last part before pseudo)
        parts = selector.split()
        base = parts[-1] if parts else selector
        
        # If base has a class or id, attach attribute to it
        if '.' in base or '#' in base:
            # Find the element part (before class or id)
            match = re.match(r'^([a-zA-Z][a-zA-Z0-9]*)?([.#][^.#]+)*$', base)
            if match:
                element = match.group(1) or ''
                # Add attribute to the element part
                if element:
                    new_base = f"{element}[{scope_id}]{base[len(element):]}"
                else:
                    new_base = f"{base}[{scope_id}]"
                
                parts[-1] = new_base
                return ' '.join(parts)
        
        # Default: add attribute to the selector
        return f"{selector}[{scope_id}]"
    
    def _generate_scope_id(self, component_name: str) -> str:
        """Generate a unique scope ID for a component."""
        # Hash the component name to create a stable ID
        hash_bytes = hashlib.sha256(component_name.encode()).digest()
        hash_hex = hash_bytes.hex()[:8]
        return f"data-v-{component_name.lower()[:10]}-{hash_hex}"


class StyleParser:
    """
    Parses the style section of a .vel component.
    """
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def parse(self, source: str, filename: str = "<input>", scoped: bool = False) -> ComponentStyle:
        """
        Parse the style section into a ComponentStyle object.
        
        Args:
            source: The style source code
            filename: The source filename
            scoped: Whether the style is scoped
            
        Returns:
            A ComponentStyle object.
        """
        self.errors = []
        self.warnings = []
        
        if not source or not source.strip():
            return ComponentStyle(css="", scoped=scoped)
        
        # Parse CSS to validate
        parser = CSSParser()
        stylesheet = parser.parse(source)
        
        if parser.errors:
            self.errors.extend(parser.errors)
        
        # Validate CSS
        css = source.strip()
        
        # Check for common issues
        self._validate_css(css)
        
        # If scoped, we'll scope it later (during generation)
        return ComponentStyle(
            css=css,
            scoped=scoped,
            line=0,  # Would need to track line number
        )
    
    def _validate_css(self, css: str):
        """Validate CSS for common issues."""
        # Check for unclosed braces
        open_braces = css.count('{')
        close_braces = css.count('}')
        if open_braces != close_braces:
            self.warnings.append(f"Unbalanced braces: {open_braces} opening, {close_braces} closing")
        
        # Check for missing semicolons
        # Simple check: look for property: value patterns without semicolon before }
        import re
        bad_pattern = r'([a-zA-Z-]+)\s*:\s*[^;}]+\s*(?=\})'
        matches = re.findall(bad_pattern, css)
        if matches:
            self.warnings.append(f"Possible missing semicolons before closing brace: {matches[:3]}")
        
        # Check for empty rules
        empty_rule_pattern = r'[^{]+\{\s*\}'
        empty_matches = re.findall(empty_rule_pattern, css)
        if empty_matches:
            self.warnings.append(f"Empty CSS rules found: {len(empty_matches)}")
    
    def scope_css(self, css: str, component_name: str, scope_id: str = None) -> str:
        """
        Scope CSS with a unique component ID.
        
        Args:
            css: The CSS source
            component_name: The component name
            scope_id: Optional custom scope ID
            
        Returns:
            Scoped CSS
        """
        if not css or not css.strip():
            return ""
        
        scoper = CSSScoper()
        return scoper.scope(css, component_name, scope_id)