"""
Project discovery - discovers project structure and configuration.

Finds project root, configuration files, and builds project structure.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import os


class ProjectDiscovery:
    """
    Discovers project structure and configuration.
    """
    
    def __init__(self):
        self.root_dir: Optional[Path] = None
        self.config_file: Optional[Path] = None
        self.config: Dict[str, Any] = {}
    
    def discover(self, start_dir: str | Path = None) -> Dict[str, Any]:
        """
        Discover project structure.
        
        Args:
            start_dir: The starting directory for discovery.
            
        Returns:
            A dictionary with project information.
        """
        if start_dir is None:
            start_dir = os.getcwd()
        
        start = Path(start_dir)
        
        # Find project root
        self.root_dir = self._find_root(start)
        
        # Find configuration
        self.config_file = self._find_config()
        
        # Load configuration
        if self.config_file:
            self.config = self._load_config()
        
        # Build project structure
        project_info = {
            'root': str(self.root_dir) if self.root_dir else None,
            'config_file': str(self.config_file) if self.config_file else None,
            'config': self.config,
            'has_config': self.config_file is not None,
        }
        
        return project_info
    
    def _find_root(self, start: Path) -> Optional[Path]:
        """Find the project root directory."""
        current = start
        
        while current != current.parent:
            # Check for common project markers
            markers = [
                current / 'package.json',
                current / 'pyproject.toml',
                current / 'setup.py',
                current / 'requirements.txt',
                current / 'templates',
                current / 'static',
                current / 'src',
            ]
            
            for marker in markers:
                if marker.exists():
                    return current
            
            current = current.parent
        
        return start
    
    def _find_config(self) -> Optional[Path]:
        """Find the configuration file."""
        if not self.root_dir:
            return None
        
        config_names = [
            'teloce.config.json',
            'teloce.config.js',
            'teloce.config.ts',
            '.telocerc',
            'veloce.config.json',
        ]
        
        for name in config_names:
            config_path = self.root_dir / name
            if config_path.exists():
                return config_path
        
        return None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the configuration file."""
        if not self.config_file:
            return {}
        
        try:
            if self.config_file.suffix == '.json' or self.config_file.name == '.telocerc':
                with open(self.config_file) as f:
                    return json.load(f)
            else:
                # For JS/TS config files, we would need to parse them
                # For now, return empty dict
                return {}
        except Exception:
            return {}
    
    def get_project_name(self) -> str:
        """Get the project name."""
        if not self.root_dir:
            return 'unknown'
        return self.root_dir.name
    
    def get_static_dir(self) -> Optional[Path]:
        """Get the static directory."""
        if not self.root_dir:
            return None
        
        static_dirs = ['static', 'public', 'assets']
        for dir_name in static_dirs:
            static_dir = self.root_dir / dir_name
            if static_dir.exists():
                return static_dir
        
        return None
    
    def get_templates_dir(self) -> Optional[Path]:
        """Get the templates directory."""
        if not self.root_dir:
            return None
        
        templates_dir = self.root_dir / 'templates'
        if templates_dir.exists():
            return templates_dir
        
        return None
    
    def get_js_dir(self) -> Optional[Path]:
        """Get the JavaScript directory."""
        static_dir = self.get_static_dir()
        if not static_dir:
            return None
        
        js_dirs = ['js', 'javascript', 'scripts']
        for dir_name in js_dirs:
            js_dir = static_dir / dir_name
            if js_dir.exists():
                return js_dir
        
        return None