"""
Module generator - generates JavaScript module code.
"""

from typing import List, Optional, Dict, Any


class ModuleGenerator:
    """
    Generates JavaScript module code.
    """
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}
        self.minify = self.options.get('minify', False)
    
    def generate_module(self, name: str, content: str, exports: List[str] = None) -> str:
        """Generate a complete module."""
        lines = []
        
        lines.append(f'// Module: {name}')
        lines.append('')
        lines.append(content)
        lines.append('')
        
        if exports:
            lines.append(f'export {{ {", ".join(exports)} }};')
        
        return '\n'.join(lines)
    
    def generate_iife(self, name: str, code: str) -> str:
        """Generate an IIFE (Immediately Invoked Function Expression)."""
        lines = []
        lines.append(f'const {name} = (function() {{')
        lines.append('  const exports = {};')
        lines.append('')
        for line in code.split('\n'):
            lines.append(f'  {line}')
        lines.append('')
        lines.append('  return exports;')
        lines.append('})();')
        return '\n'.join(lines)
    
    def generate_umd(self, name: str, code: str) -> str:
        """Generate a UMD (Universal Module Definition) module."""
        lines = []
        lines.append(f'(function(root, factory) {{')
        lines.append('  if (typeof define === "function" && define.amd) {')
        lines.append('    define([], factory);')
        lines.append('  } else if (typeof exports === "object") {')
        lines.append('    module.exports = factory();')
        lines.append('  } else {')
        lines.append(f'    root.{name} = factory();')
        lines.append('  }')
        lines.append('})(this, function() {')
        lines.append('')
        lines.append('  const exports = {};')
        for line in code.split('\n'):
            lines.append(f'  {line}')
        lines.append('')
        lines.append('  return exports;')
        lines.append('});')
        return '\n'.join(lines)
