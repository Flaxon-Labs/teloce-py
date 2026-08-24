"""
Project paths - manages project paths.

Provides utilities for working with project paths.
"""

from pathlib import Path
from typing import Optional, List, Union


class ProjectPaths:
    """
    Manages project paths.
    """
    
    def __init__(self, root_dir: str | Path = None):
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
        self._static_dir: Optional[Path] = None
        self._templates_dir: Optional[Path] = None
        self._js_dir: Optional[Path] = None
        self._build_dir: Optional[Path] = None
    
    def set_root(self, root_dir: str | Path) -> None:
        """Set the project root directory."""
        self.root_dir = Path(root_dir)
        self._clear_cache()
    
    def _clear_cache(self) -> None:
        """Clear cached path values."""
        self._static_dir = None
        self._templates_dir = None
        self._js_dir = None
        self._build_dir = None
    
    def get_static_dir(self) -> Optional[Path]:
        """Get the static directory."""
        if self._static_dir:
            return self._static_dir
        
        static_dirs = ['static', 'public', 'assets']
        for dir_name in static_dirs:
            static_dir = self.root_dir / dir_name
            if static_dir.exists():
                self._static_dir = static_dir
                return static_dir
        
        return None
    
    def get_templates_dir(self) -> Optional[Path]:
        """Get the templates directory."""
        if self._templates_dir:
            return self._templates_dir
        
        templates_dir = self.root_dir / 'templates'
        if templates_dir.exists():
            self._templates_dir = templates_dir
            return templates_dir
        
        return None
    
    def get_js_dir(self) -> Optional[Path]:
        """Get the JavaScript directory."""
        if self._js_dir:
            return self._js_dir
        
        static_dir = self.get_static_dir()
        if not static_dir:
            return None
        
        js_dirs = ['js', 'javascript', 'scripts']
        for dir_name in js_dirs:
            js_dir = static_dir / dir_name
            if js_dir.exists():
                self._js_dir = js_dir
                return js_dir
        
        return None
    
    def get_build_dir(self) -> Path:
        """Get the build output directory."""
        if self._build_dir:
            return self._build_dir
        
        self._build_dir = self.root_dir / 'dist'
        return self._build_dir
    
    def get_vel_files(self) -> List[Path]:
        """Get all .vel files in the project."""
        js_dir = self.get_js_dir()
        if not js_dir:
            return []
        
        return list(js_dir.rglob('*.vel'))
    
    def get_component_dirs(self) -> List[Path]:
        """Get component directories."""
        js_dir = self.get_js_dir()
        if not js_dir:
            return []
        
        dirs = [js_dir]
        components_dir = js_dir / 'components'
        if components_dir.exists():
            dirs.append(components_dir)
        
        return dirs
    
    def get_output_path(self, vel_file: Path) -> Path:
        """Get the output path for a .vel file."""
        js_dir = self.get_js_dir()
        if not js_dir:
            return vel_file.with_suffix('.js')
        
        relative = vel_file.relative_to(js_dir)
        return (self.get_build_dir() / relative).with_suffix('.js')
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        for dir_path in [self.get_static_dir(), self.get_templates_dir(), 
                         self.get_js_dir(), self.get_build_dir()]:
            if dir_path:
                dir_path.mkdir(parents=True, exist_ok=True)