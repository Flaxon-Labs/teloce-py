"""
CSS Scoper - scopes CSS selectors to components.

Adds unique scope attributes to CSS selectors for component isolation.
"""

import re
from typing import List, Optional, Set, Tuple
from teloce.css.parser import CSSParser, CSSRule, CSSAtRule, CSSStylesheet, CSSDeclaration


class CSSScoper:
    """
    Scopes CSS selectors with a unique component ID.
    """
    
    def __init__(self):
        self.errors: List[str] = []
    
    def scope(self, css: str, scope_id: str) -> str:
        """
        Scope CSS with a unique component ID.
        
        Args:
            css: The CSS source
            scope_id: The unique scope ID (e.g., 'data-v-abc123')
            
        Returns:
            Scoped CSS.
        """
        self.errors = []
        
        if not css or not css.strip():
            return ""
        
        # Parse the CSS
        parser = CSSParser()
        stylesheet = parser.parse(css)
        
        if parser.errors:
            self.errors.extend(parser.errors)
            return css
        
        # Scope the rules
        scoped_rules = []
        
        for rule in stylesheet.rules:
            scoped_selector = self._scope_selector(rule.selector, scope_id)
            if scoped_selector:
                declarations = self._format_declarations(rule.declarations)
                scoped_rules.append(f"{scoped_selector} {{ {declarations} }}")
        
        for at_rule in stylesheet.at_rules:
            scoped_at_rule = self._scope_at_rule(at_rule, scope_id)
            if scoped_at_rule:
                scoped_rules.append(scoped_at_rule)
        
        return '\n'.join(scoped_rules)
    
    def _scope_selector(self, selector: str, scope_id: str) -> str:
        """Scope a single CSS selector."""
        if not selector or selector == '':
            return f"[{scope_id}]"
        
        # Handle keyframes (don't scope)
        if selector.startswith('@keyframes'):
            return selector
        
        # Split only on top-level commas. Commas inside functional pseudo
        # classes, attribute selectors, strings, or escaped text are part of
        # the selector and must not create a new rule.
        parts = self._split_selector_list(selector)
        scoped_parts = []
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            scoped_part = self._scope_selector_part(part, scope_id)
            if scoped_part:
                scoped_parts.append(scoped_part)
        
        return ', '.join(scoped_parts)

    def _split_selector_list(self, selector: str) -> List[str]:
        """Split a selector list while respecting CSS nesting syntax."""
        parts: List[str] = []
        start = 0
        depth = 0
        quote = ''
        escaped = False
        for index, character in enumerate(selector):
            if escaped:
                escaped = False
                continue
            if character == '\\':
                escaped = True
                continue
            if quote:
                if character == quote:
                    quote = ''
                continue
            if character in "'\"":
                quote = character
            elif character in '([':
                depth += 1
            elif character in ')]':
                depth = max(0, depth - 1)
            elif character == ',' and depth == 0:
                parts.append(selector[start:index].strip())
                start = index + 1
        parts.append(selector[start:].strip())
        return [part for part in parts if part]
    
    def _scope_selector_part(self, selector: str, scope_id: str) -> str:
        """Scope a single selector part."""
        # Vue/Teloce-compatible escape hatches.  Global and deep selectors
        # deliberately do not receive the component attribute themselves,
        # while the local prefix remains scoped.
        deep = re.search(r':deep\(([^()]*)\)', selector)
        if deep:
            prefix = selector[:deep.start()].strip()
            suffix = selector[deep.end():].strip()
            local = self._scope_selector_part(prefix, scope_id) if prefix else ""
            result = " ".join(part for part in (local, deep.group(1).strip(), suffix) if part)
            return result

        global_match = re.search(r':global\(([^()]*)\)', selector)
        if global_match:
            prefix = selector[:global_match.start()].strip()
            suffix = selector[global_match.end():].strip()
            local = self._scope_selector_part(prefix, scope_id) if prefix else ""
            if suffix:
                local_suffix = self._scope_selector_part(suffix, scope_id)
                return " ".join(part for part in (local, global_match.group(1).strip(), local_suffix) if part)
            return " ".join(part for part in (local, global_match.group(1).strip()) if part)

        slotted = re.fullmatch(r':slotted\(([^()]*)\)', selector.strip())
        if slotted:
            return f'[{scope_id}] > {slotted.group(1).strip()}'

        # Handle pseudo-classes and pseudo-elements
        # Split by : but keep the base selector
        
        # Find the base selector (before any pseudo-class)
        base_match = re.match(r'^([^:]+)', selector)
        if not base_match:
            return selector
        
        base = base_match.group(1)
        pseudo = selector[len(base):]
        
        if not base or base == '':
            # Empty base, just add attribute
            return f"[{scope_id}]{pseudo}"
        
        # Check if selector is a tag with no class or id
        if re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', base):
            # Simple tag selector
            return f"{base}[{scope_id}]{pseudo}"
        
        # Check for class or id selectors
        if '.' in base or '#' in base:
            # Find the element part (before class or id)
            match = re.match(r'^([a-zA-Z][a-zA-Z0-9]*)?([.#][^.#]+)*$', base)
            if match:
                element = match.group(1) or ''
                if element:
                    return f"{element}[{scope_id}]{base[len(element):]}{pseudo}"
                else:
                    return f"{base}[{scope_id}]{pseudo}"
        
        # Default: add attribute to the end of the selector
        return f"{base}[{scope_id}]{pseudo}"
    
    def _scope_at_rule(self, at_rule: CSSAtRule, scope_id: str) -> Optional[str]:
        """Scope an at-rule."""
        if at_rule.name in ('import', 'charset', 'namespace', 'layer') and not at_rule.rules and not at_rule.declarations:
            return f"@{at_rule.name} {at_rule.value};"

        if at_rule.name in ('keyframes', '-webkit-keyframes', '-moz-keyframes'):
            # Keyframe selectors describe animation progress, not DOM nodes.
            frames = []
            for rule in at_rule.rules:
                frames.append(f"{rule.selector} {{ {self._format_declarations(rule.declarations)} }}")
            return f"@{at_rule.name} {at_rule.value} {{ {' '.join(frames)} }}"

        if at_rule.declarations:
            declarations = self._format_declarations(at_rule.declarations)
            return f"@{at_rule.name} {at_rule.value} {{ {declarations} }}"

        if at_rule.rules or at_rule.nested_at_rules:
            # Scope nested rules
            scoped_rules = []
            for rule in at_rule.rules:
                scoped_selector = self._scope_selector(rule.selector, scope_id)
                if scoped_selector:
                    declarations = self._format_declarations(rule.declarations)
                    scoped_rules.append(f"{scoped_selector} {{ {declarations} }}")

            for nested in at_rule.nested_at_rules:
                rendered = self._scope_at_rule(nested, scope_id)
                if rendered:
                    scoped_rules.append(rendered)
            
            if scoped_rules:
                scoped_body = '\n'.join(scoped_rules)
                return f"@{at_rule.name} {at_rule.value} {{ {scoped_body} }}"
        
        return None
    
    def _format_declarations(self, declarations: List[CSSDeclaration]) -> str:
        """Format declarations as a string."""
        if not declarations:
            return ""
        
        return '; '.join(f"{decl.property}: {decl.value}" for decl in declarations)
    
    def _get_scope_id(self, component_name: str, hashed: bool = True) -> str:
        """Generate a scope ID."""
        if hashed:
            import hashlib
            hash_val = hashlib.md5(component_name.encode()).hexdigest()[:8]
            return f"data-v-{hash_val}"
        return f"data-v-{component_name.lower()}"
