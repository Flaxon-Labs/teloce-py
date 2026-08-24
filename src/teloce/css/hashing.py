"""
Hash Generator - generates unique hashes for scoped CSS.

Provides consistent hash generation for component scope IDs.
"""

import hashlib
from typing import Optional


class HashGenerator:
    """
    Generates unique hashes for scoped CSS.
    """
    
    def __init__(self):
        self.cache: dict = {}
    
    def generate(self, component_name: str, length: int = 8) -> str:
        """
        Generate a unique hash for a component name.
        
        Args:
            component_name: The component name
            length: The hash length
            
        Returns:
            A unique hash string.
        """
        # Check cache
        cache_key = f"{component_name}:{length}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Generate hash
        hash_val = hashlib.md5(component_name.encode()).hexdigest()
        result = hash_val[:length]
        
        # Cache the result
        self.cache[cache_key] = result
        
        return result
    
    def generate_scope_id(self, component_name: str, prefix: str = "data-v") -> str:
        """
        Generate a scope ID for a component.
        
        Args:
            component_name: The component name
            prefix: The scope ID prefix
            
        Returns:
            A scope ID string.
        """
        hash_val = self.generate(component_name, length=9)
        return f"{prefix}-{hash_val}"
    
    def generate_selector(self, component_name: str) -> str:
        """
        Generate a scoped selector attribute.
        
        Args:
            component_name: The component name
            
        Returns:
            A scoped selector attribute.
        """
        scope_id = self.generate_scope_id(component_name)
        return f"[{scope_id}]"
    
    def clear_cache(self):
        """Clear the hash cache."""
        self.cache.clear()
