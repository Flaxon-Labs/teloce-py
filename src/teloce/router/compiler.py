"""
Router compiler - compiles router configuration.

Parses and validates router configuration for client-side routing.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Route:
    """A route definition."""
    path: str
    component: str
    name: Optional[str] = None
    children: List['Route'] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
    props: bool = False
    redirect: Optional[str] = None


@dataclass
class RouterConfig:
    """Router configuration."""
    routes: List[Route] = field(default_factory=list)
    mode: str = "hash"  # hash | history
    base: str = "/"
    link_active_class: str = "active"
    link_exact_active_class: str = "exact-active"


class RouterCompiler:
    """
    Compiles router configuration.
    
    Parses and validates route definitions.
    """
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def compile(self, config: Dict[str, Any]) -> Optional[RouterConfig]:
        """
        Compile router configuration.
        
        Args:
            config: The router configuration dictionary
            
        Returns:
            A RouterConfig object or None if compilation fails.
        """
        self.errors = []
        self.warnings = []
        
        if not config:
            self.errors.append("Router configuration is empty")
            return None
        
        # Extract routes
        mode = config.get('mode', 'hash')
        if mode not in {'hash', 'history'}:
            self.errors.append("Router mode must be 'hash' or 'history'")
        routes_data = config.get('routes', [])
        if not isinstance(routes_data, list):
            self.errors.append("Router 'routes' must be a list")
            return None
        if not routes_data:
            self.errors.append("No routes defined")
            return None
        
        routes = self._parse_routes(routes_data)
        if not routes:
            self.errors.append("Failed to parse routes")
            return None
        
        # Validate routes
        self._validate_routes(routes)
        
        if self.errors:
            return None
        
        return RouterConfig(
            routes=routes,
            mode=mode,
            base=config.get('base', '/'),
            link_active_class=config.get('link_active_class', 'active'),
            link_exact_active_class=config.get('link_exact_active_class', 'exact-active'),
        )
    
    def _parse_routes(self, routes_data: List[Dict[str, Any]], prefix: str = "") -> List[Route]:
        """Parse route definitions."""
        routes = []
        
        for route_data in routes_data:
            path = route_data.get('path', '')
            component = route_data.get('component', '')
            name = route_data.get('name')
            children_data = route_data.get('children', [])
            meta = route_data.get('meta', {})
            props = route_data.get('props', False)
            redirect = route_data.get('redirect')
            
            if not path:
                self.errors.append("Route missing 'path' field")
                continue
            
            if not component and not redirect:
                self.errors.append(f"Route '{path}' missing 'component' or 'redirect' field")
                continue
            
            # Normalize path
            if prefix and path:
                if path.startswith('/'):
                    full_path = path
                else:
                    full_path = f"{prefix}/{path}" if prefix != '/' else f"/{path}"
            else:
                full_path = path if path.startswith('/') else f"/{path}"
            
            # Parse children
            children = []
            if children_data:
                children = self._parse_routes(children_data, full_path)
            
            route = Route(
                path=full_path,
                component=component,
                name=name,
                children=children,
                meta=meta,
                props=props,
                redirect=redirect,
            )
            routes.append(route)
        
        return routes
    
    def _validate_routes(self, routes: List[Route], parent_path: str = "") -> None:
        """Validate routes for common issues."""
        names = set()
        paths = set()
        for route in routes:
            if route.name:
                if route.name in names:
                    self.errors.append(f"Duplicate route name '{route.name}'")
                names.add(route.name)
            if route.path in paths:
                self.errors.append(f"Duplicate route path '{route.path}'")
            paths.add(route.path)
            if not route.component and not route.redirect:
                self.warnings.append(f"Route '{route.path}' has no component or redirect")
            
            # Validate children
            if route.children:
                self._validate_routes(route.children, route.path)
    
    def has_errors(self) -> bool:
        """Check if there are compilation errors."""
        return len(self.errors) > 0
