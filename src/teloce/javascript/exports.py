"""
Export generator - generates JavaScript export statements.
"""

from typing import List, Optional, Dict, Any


class ExportGenerator:
    """
    Generates JavaScript export statements.
    """
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}
        self.minify = self.options.get('minify', False)
    
    def generate_default_export(self, name: str, value: str) -> str:
        """Generate a default export."""
        if self.minify:
            return f'export default {value}'
        return f'export default {value};'
    
    def generate_named_export(self, name: str, value: Optional[str] = None) -> str:
        """Generate a named export."""
        if value:
            return f'export const {name} = {value};'
        # ``export const name;`` is invalid JavaScript.  An uninitialised
        # public binding has a deterministic undefined value instead.
        return f'export const {name} = undefined;'
    
    def generate_export_list(self, names: List[str]) -> str:
        """Generate an export list."""
        if self.minify:
            return f'export {{{",".join(names)}}}'
        return f'export {{{", ".join(names)}}}'
    
    def generate_component_export(self, component_name: str) -> str:
        """Generate a component export."""
        return f'export default {component_name};'
    
    def generate_all_exports(self, exports: Dict[str, str]) -> str:
        """Generate multiple exports."""
        lines = []
        for name, value in exports.items():
            if name == 'default':
                lines.append(self.generate_default_export(name, value))
            else:
                lines.append(self.generate_named_export(name, value))
        return '\n'.join(lines)
