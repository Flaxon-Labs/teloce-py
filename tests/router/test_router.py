"""
Tests for the router module.
"""

import subprocess
import tempfile
from pathlib import Path

import pytest

from teloce.router.compiler import RouterCompiler, Route, RouterConfig
from teloce.router.generator import RouterGenerator


class TestRouter:
    """Tests for the router."""

    def test_route_creation(self):
        """Test route creation."""
        route = Route(path='/', component='HomePage')
        assert route.path == '/'
        assert route.component == 'HomePage'

    def test_router_compiler_basic(self):
        """Test basic router compilation."""
        compiler = RouterCompiler()
        config = {
            'routes': [
                {'path': '/', 'component': 'HomePage'},
                {'path': '/about', 'component': 'AboutPage'},
            ]
        }
        result = compiler.compile(config)
        
        assert result is not None
        assert len(result.routes) == 2
        assert result.routes[0].path == '/'
        assert result.routes[0].component == 'HomePage'

    def test_router_compiler_with_children(self):
        """Test router compilation with children."""
        compiler = RouterCompiler()
        config = {
            'routes': [
                {
                    'path': '/dashboard',
                    'component': 'Dashboard',
                    'children': [
                        {'path': '/', 'component': 'Overview'},
                        {'path': '/profile', 'component': 'Profile'},
                    ]
                }
            ]
        }
        result = compiler.compile(config)
        
        assert result is not None
        assert len(result.routes) == 1
        assert len(result.routes[0].children) == 2

    def test_router_compiler_with_redirect(self):
        """Test router compilation with redirect."""
        compiler = RouterCompiler()
        config = {
            'routes': [
                {'path': '/', 'redirect': '/home'},
                {'path': '/home', 'component': 'HomePage'},
            ]
        }
        result = compiler.compile(config)
        
        assert result is not None
        assert result.routes[0].redirect == '/home'

    def test_router_generator(self):
        """Test router generator."""
        config = RouterConfig(
            routes=[
                Route(path='/', component='HomePage'),
                Route(path='/about', component='AboutPage'),
            ]
        )
        generator = RouterGenerator()
        code = generator.generate(config)
        
        assert 'routes' in code
        assert 'HomePage' in code
        assert 'AboutPage' in code
        assert 'createRouter' in code
        assert "const createRouter =" in code
        assert "from '@teloce/router'" not in code

    def test_router_rejects_invalid_route_shapes_and_global_duplicates(self):
        compiler = RouterCompiler()
        assert compiler.compile({"routes": ["not-an-object"]}) is None
        assert "Each route must be an object" in compiler.errors

        result = compiler.compile({"routes": [
            {"path": "/one", "component": "One", "name": "same"},
            {"path": "/parent", "component": "Parent", "children": [
                {"path": "child", "component": "Child", "name": "same"}
            ]},
        ]})
        assert result is None
        assert any("Duplicate route name" in error for error in compiler.errors)

    def test_router_generator_serializes_meta_and_hardens_navigation(self):
        config = RouterConfig(routes=[Route(
            path="/app/:id",
            component="Pages.App",
            meta={"requiresAuth": False, "nested": {"roles": ["reader"]}},
        )], mode="history", base="/base")
        code = RouterGenerator().generate(config)
        assert '"requiresAuth":false' in code
        assert "redirect cycle detected" in code
        assert '`${base}/${path.replace' in code
        assert "router.destroy?.()" not in code

        with tempfile.NamedTemporaryFile("w", suffix=".mjs", encoding="utf-8", delete=False) as handle:
            handle.write("const Pages = {App: {}};\n" + code)
            path = Path(handle.name)
        try:
            checked = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
            assert checked.returncode == 0, checked.stderr
        finally:
            path.unlink(missing_ok=True)
