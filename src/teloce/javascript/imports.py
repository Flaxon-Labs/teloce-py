"""
Import generator - generates JavaScript import statements.
"""

from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass


@dataclass
class ImportStatement:
    """Represents an import statement."""
    source: str
    names: List[str]
    default_name: Optional[str] = None
    namespace_name: Optional[str] = None
    is_type: bool = False
    
    def to_string(self, minify: bool = False) -> str:
        """Convert to import statement string."""
        parts = []
        
        if self.default_name:
            parts.append(self.default_name)
        
        if self.names:
            names = ', '.join(self.names)
            if self.default_name:
                parts.append(f'{{ {names} }}')
            else:
                parts.append(f'{{ {names} }}')
        
        if self.namespace_name:
            parts.append(f'* as {self.namespace_name}')
        
        if not parts:
            return f'import "{self.source}"'
        
        return f'import {", ".join(parts)} from "{self.source}"'


class ImportGenerator:
    """
    Generates JavaScript import statements.
    """
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}
        self.minify = self.options.get('minify', False)
        self.imports: Dict[str, ImportStatement] = {}
    
    def add_import(self, source: str, name: str, is_default: bool = False, 
                   is_namespace: bool = False, is_type: bool = False) -> None:
        """Add an import."""
        if source not in self.imports:
            self.imports[source] = ImportStatement(source=source, names=[], is_type=is_type)
        
        imp = self.imports[source]
        
        if is_default:
            imp.default_name = name
        elif is_namespace:
            imp.namespace_name = name
        else:
            if name not in imp.names:
                imp.names.append(name)
    
    def generate(self) -> str:
        """Generate all import statements."""
        if not self.imports:
            return ''
        
        statements = []
        for imp in self.imports.values():
            statements.append(imp.to_string(self.minify))
        
        return '\n'.join(statements)
    
    def generate_for_component(self, component_name: str, source: str) -> str:
        """Generate import for a component."""
        return f'import {component_name} from "{source}"'
    
    def generate_runtime_imports(self) -> str:
        """Generate runtime imports."""
        imports = [
            'createSignal',
            'createEffect',
            'createComputed',
            'createComponent',
            'mount',
            'unmount',
        ]
        
        if self.minify:
            return f'import {{{",".join(imports)}}} from "teloce"'
        return f'import {{{", ".join(imports)}}} from "teloce"'