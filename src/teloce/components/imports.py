"""
Component importer - handles component imports.

Manages import statements and component resolution.
"""

import re
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path


class ComponentImporter:
    """
    Handles component imports and resolution.
    """
    
    def __init__(self):
        self.imports: Dict[str, str] = {}  # alias -> source
        self.components: Dict[str, str] = {}  # name -> source
        self.import_lines: List[str] = []
    
    def parse_import(self, line: str) -> Optional[Tuple[str, str]]:
        """
        Parse an import statement.
        
        Args:
            line: The import line
            
        Returns:
            A tuple of (name, source) or None.
        """
        # Default import: import X from 'source'
        default_match = re.match(r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]', line)
        if default_match:
            name = default_match.group(1)
            source = default_match.group(2)
            self.imports[name] = source
            self.components[name] = source
            return (name, source)
        
        # Named import: import { X, Y } from 'source'
        named_match = re.match(r'import\s*{([^}]+)}\s*from\s+[\'"]([^\'"]+)[\'"]', line)
        if named_match:
            names_str = named_match.group(1)
            source = named_match.group(2)
            for name_part in names_str.split(','):
                name = name_part.strip()
                if name:
                    self.imports[name] = source
                    self.components[name] = source
            return None
        
        # Namespace import: import * as X from 'source'
        namespace_match = re.match(r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]', line)
        if namespace_match:
            name = namespace_match.group(1)
            source = namespace_match.group(2)
            self.imports[name] = source
            self.components[name] = source
            return (name, source)
        
        return None
    
    def add_import(self, name: str, source: str):
        """Add an import."""
        self.imports[name] = source
        self.components[name] = source
    
    def get_import(self, name: str) -> Optional[str]:
        """Get the import source for a name."""
        return self.imports.get(name)
    
    def get_component(self, name: str) -> Optional[str]:
        """Get the component source for a name."""
        return self.components.get(name)
    
    def generate_imports(self) -> str:
        """Generate import statements."""
        return '\n'.join(self.import_lines)
    
    def clear(self):
        """Clear all imports."""
        self.imports.clear()
        self.components.clear()
        self.import_lines.clear()
    
    def from_script(self, script: str) -> List[Tuple[str, str]]:
        """
        Extract imports from a script.
        
        Args:
            script: The script source code
            
        Returns:
            A list of (name, source) tuples.
        """
        imports = []
        
        # Find all import statements
        import_pattern = r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, script):
            name = match.group(1)
            source = match.group(2)
            imports.append((name, source))
            self.add_import(name, source)
        
        # Named imports
        named_pattern = r'import\s*{([^}]+)}\s*from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(named_pattern, script):
            names_str = match.group(1)
            source = match.group(2)
            for name_part in names_str.split(','):
                name = name_part.strip()
                if name:
                    imports.append((name, source))
                    self.add_import(name, source)
        
        return imports