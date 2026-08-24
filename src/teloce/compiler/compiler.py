"""
Main compiler orchestrator.

This module coordinates the entire compilation pipeline:
1. Lexical analysis (Lexer)
2. Parsing (Parser)
3. Transformation (Transformer)
4. Optimization (Optimizer)
5. JavaScript generation (Generator)
"""

from pathlib import Path
from typing import Optional, List, Dict, Any

from teloce.compiler.lexer import Lexer, Token
from teloce.compiler.parser import Parser
from teloce.compiler.transformer import Transformer
from teloce.compiler.optimizer import Optimizer
from teloce.compiler.generator import Generator
from teloce.compiler.diagnostics import Diagnostics, DiagnosticLevel
from teloce.compiler.source_map import SourceMapGenerator
from teloce.sfc.parser import SFCParser
from teloce.sfc.component import Component


class Compiler:
    """
    Main compiler class that orchestrates the compilation pipeline.
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}
        self.plugin_registry = self.options.get("plugin_registry")
        self.diagnostics = Diagnostics()

        # Accept both spellings used by the CLI and public API.
        self.source_map_enabled = self.options.get(
            "source_map",
            self.options.get("source_maps", True),
        )
        self.minify = self.options.get("minify", False)
        self.dev = self.options.get("dev", True)

    def compile(self, source: str, filename: str = "<input>") -> Dict[str, Any]:
        """Compile source and convert unexpected compiler failures to diagnostics.

        A malformed component must never bring down a dev server or a batch
        build.  Expected syntax errors are already reported by the individual
        pipeline stages; this boundary also protects callers from an internal
        parser/generator exception and returns the same stable result shape.
        """
        try:
            return self._compile(source, filename)
        except Exception as exc:  # pragma: no cover - exercised by integration smoke tests
            self.diagnostics = Diagnostics()
            self.diagnostics.add(
                DiagnosticLevel.ERROR,
                f"Compilation failed: {exc}",
                filename=filename,
                code="E1000",
            )
            return self._empty_result()

    def _compile(self, source: str, filename: str = "<input>") -> Dict[str, Any]:
        """
        Compile a .vel file from source string.
        
        Args:
            source: The .vel file content
            filename: The source filename (for error reporting)
            
        Returns:
            Dict containing:
                - code: Generated JavaScript
                - css: Extracted CSS
                - map: Source map (if enabled)
                - diagnostics: Compilation messages
                - ast: Abstract Syntax Tree
        """
        self.diagnostics = Diagnostics()
        source = self._run_plugin_hooks("before_compile", source)

        # Step 1: Parse SFC
        sfc_parser = SFCParser()
        component = sfc_parser.parse(source, filename)
        
        if not component:
            for error in sfc_parser.errors:
                self.diagnostics.add(DiagnosticLevel.ERROR, error, filename=filename)
            for warning in sfc_parser.warnings:
                self.diagnostics.add(DiagnosticLevel.WARNING, warning, filename=filename)
            self.diagnostics.add(
                DiagnosticLevel.ERROR,
                "Failed to parse SFC",
                filename=filename
            )
            return self._empty_result()

        # SFCParser already lexes and parses the template. Keeping one
        # canonical template AST avoids parsing the AST as if it were text.
        ast = component.template

        ast = self._run_plugin_hooks("before_transform", ast)

        # Step 2: Transformation
        transformer = Transformer()
        transformed_ast = transformer.transform(ast)
        
        if transformer.has_errors:
            for error in transformer.errors:
                self.diagnostics.add(
                    DiagnosticLevel.ERROR,
                    error,
                    filename=filename
                )
            return self._empty_result()

        # Step 3: Optimization
        optimizer = Optimizer(self.options)
        optimized_ast = optimizer.optimize(transformed_ast)

        # Step 4: Code generation
        generator_options = dict(self.options)
        filter_registry = generator_options.get("filter_registry")
        if filter_registry and hasattr(filter_registry, "get_js_filters"):
            generator_options["filter_js"] = filter_registry.get_js_filters()
        if self.plugin_registry and hasattr(self.plugin_registry, "get_api"):
            plugin_api = self.plugin_registry.get_api()
            if plugin_api and hasattr(plugin_api, "get_js_filters"):
                generator_options["filter_js"] = {
                    **generator_options.get("filter_js", {}),
                    **plugin_api.get_js_filters(),
                }
        generator = Generator(generator_options)
        js_code = generator.generate(optimized_ast, component)
        js_code = self._run_plugin_hooks("after_compile", js_code)
        css_code = self._generate_css(component)

        # Step 5: Source map generation
        source_map = None
        if self.source_map_enabled:
            source_map_generator = SourceMapGenerator()
            source_map = source_map_generator.generate(js_code, filename, source)

        return {
            "code": js_code,
            "css": css_code,
            "map": source_map,
            "diagnostics": self.diagnostics.to_dict(),
            "ast": optimized_ast,
            "component": component,
            "success": not self.diagnostics.has_errors(),
        }

    def _run_plugin_hooks(self, name: str, value: Any) -> Any:
        """Run optional plugin hooks without making plugins mandatory."""
        registry = self.plugin_registry
        api = registry.get_api() if registry and hasattr(registry, "get_api") else None
        if not api or not hasattr(api, "get_hooks"):
            return value
        for hook in api.get_hooks(name):
            result = hook(value)
            if result is not None:
                value = result
        return value

    def _generate_css(self, component: Component) -> str:
        """Generate CSS from component styles."""
        if not component.style:
            return ""

        from teloce.css.generator import CSSGenerator
        blocks = getattr(component, "styles", None) or [component.style]
        generated = []
        for style in blocks:
            css_options = dict(self.options)
            css_options["scoped"] = style.scoped
            css_options["module"] = style.module
            generated.append(CSSGenerator(css_options).generate(style.css, component.name))
        return "\n".join(css for css in generated if css)

    def _empty_result(self) -> Dict[str, Any]:
        """Return an empty compilation result."""
        return {
            "code": "",
            "css": "",
            "map": None,
            "diagnostics": self.diagnostics.to_dict(),
            "ast": None,
            "component": None,
            "success": False,
        }


def compile(source: str, filename: str = "<input>", **options) -> Dict[str, Any]:
    """
    Compile a .vel file from source string.
    
    Args:
        source: The .vel file content
        filename: The source filename (for error reporting)
        **options: Compiler options
        
    Returns:
        Compilation result dictionary.
    """
    compiler = Compiler(options)
    return compiler.compile(source, filename)


def compile_file(filepath: str | Path, **options) -> Dict[str, Any]:
    """
    Compile a .vel file from disk.
    
    Args:
        filepath: Path to the .vel file
        **options: Compiler options
        
    Returns:
        Compilation result dictionary.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        return {
            "code": "",
            "css": "",
            "map": None,
            "diagnostics": {
                "errors": [f"File not found: {filepath}"],
                "warnings": [],
                "info": [],
            },
            "ast": None,
            "component": None,
            "success": False,
        }

    source = filepath.read_text(encoding="utf-8")
    return compile(source, str(filepath), **options)


def compile_project(root_dir: str | Path, **options) -> Dict[str, Any]:
    """
    Compile all .vel files in a project.
    
    Args:
        root_dir: Project root directory
        **options: Compiler options
        
    Returns:
        Compilation results for all files.
    """
    root_dir = Path(root_dir)
    results = {}
    
    # Find all .vel files
    vel_files = list(root_dir.rglob("*.vel"))
    
    for vel_file in vel_files:
        rel_path = vel_file.relative_to(root_dir)
        result = compile_file(vel_file, **options)
        # Use stable POSIX-style keys on every platform for manifests and
        # reproducible project results.
        results[rel_path.as_posix()] = result
    
    return results
