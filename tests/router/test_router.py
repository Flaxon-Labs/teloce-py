"""
Tests for the router module.
"""

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
