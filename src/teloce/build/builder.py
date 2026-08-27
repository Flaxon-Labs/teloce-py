"""
Builder - builds the project.

Orchestrates the build process for .vel files.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import time
import re
import os
import shutil
import hashlib

from teloce.compiler.compiler import Compiler
from teloce.project.scanner import ProjectScanner
from teloce.build.writer import FileWriter
from teloce.build.manifest import ManifestGenerator
from teloce.build.assets import AssetManager
from teloce.components.dependency_graph import DependencyGraph
from teloce.build.bundler import ModuleBundler


class Builder:
    """
    Builds the project.
    
    Orchestrates compilation of .vel files.
    """
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}
        self.compiler = Compiler(options)
        self.writer = FileWriter()
        self.manifest = ManifestGenerator()
        self.scanner = ProjectScanner()
        self.dependency_graph = DependencyGraph()
        self.clean_output = bool(self.options.get("clean", False))
        self.hash_assets = bool(self.options.get("hash_assets", False))
        self.assets = AssetManager(self.hash_assets)
        
        self.root_dir: Optional[Path] = None
        self.out_dir: Optional[Path] = None
        self.stats: Dict[str, Any] = {}
    
    def build(self, root_dir: str | Path, out_dir: str | Path = None) -> Dict[str, Any]:
        """
        Build the project.
        
        Args:
            root_dir: The project root directory.
            out_dir: The output directory.
            
        Returns:
            Build statistics and results.
        """
        start_time = time.time()
        
        self.root_dir = Path(root_dir)
        self.out_dir = Path(out_dir) if out_dir else self.root_dir / 'dist'

        if self.clean_output:
            self._clean_generated_output()
        
        # Ensure output directory exists
        self.out_dir.mkdir(parents=True, exist_ok=True)
        
        # Scan for .vel files
        # The output directory is frequently inside the project (for example
        # ``public`` on Vercel).  Never treat generated .vel files there as
        # new source files on the same build.
        vel_files = self.scanner.scan(self.root_dir, exclude_paths=[self.out_dir])
        self._build_dependency_graph(vel_files)
        
        results = {
            'total': len(vel_files),
            'compiled': 0,
            'failed': 0,
            'errors': [],
            'files': [],
            'dependencies': {
                component: sorted(self.dependency_graph.get_dependencies(component))
                for component in sorted(self.dependency_graph._components)
            },
            'dependency_cycle': self.dependency_graph.has_cycle()[1],
        }
        
        # Compile each .vel file
        for vel_file in vel_files:
            try:
                result = self._compile_file(vel_file)
                results['compiled'] += 1
                results['files'].append({
                    'input': vel_file.relative_to(self.root_dir).as_posix(),
                    'output': result['output'],
                    'size': result['size'],
                })
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'file': str(vel_file),
                    'error': str(e),
                })
        
        # Copy assets
        assets_copied = self.assets.copy_assets(self.root_dir, self.out_dir)
        results['assets_copied'] = assets_copied
        results['asset_map'] = dict(self.assets.asset_map)
        self._rewrite_generated_asset_map(results)
        if self.options.get('dev', False):
            self._write_dev_entrypoint()

        if self.options.get('bundle', False) and not results['failed']:
            try:
                entry = self.options.get('bundle_entry')
                if not entry:
                    default_entry = self.out_dir / 'static' / 'js' / 'App.js'
                    entry = default_entry if default_entry.exists() else next(self.out_dir.rglob('*.js'))
                output = self.options.get('bundle_output')
                bundle_path = ModuleBundler(self.out_dir).bundle(entry, output)
                results['bundle'] = bundle_path.relative_to(self.out_dir).as_posix()
                results['files'].append({
                    'input': str(entry),
                    'output': results['bundle'],
                    'size': bundle_path.stat().st_size,
                })
            except Exception as error:
                results['failed'] += 1
                results['errors'].append({'file': str(entry), 'error': str(error)})

        # Generate the manifest after assets and optional bundling are complete.
        manifest = self.manifest.generate(results, self.out_dir)
        self.writer.write_json(self.out_dir / 'manifest.json', manifest)
        
        results['duration'] = time.time() - start_time
        self.stats = results
        
        return results

    def _rewrite_generated_asset_map(self, results: Dict[str, Any]) -> None:
        """Add generated hashed outputs to the public asset map."""
        for file_info in results.get('files', []):
            input_name = str(file_info.get('input', ''))
            output_name = str(file_info.get('output', ''))
            if input_name.endswith('.vel') and output_name:
                self.assets.asset_map[input_name[:-4] + '.js'] = output_name
                css_output = output_name[:-3] + 'css'
                if (self.out_dir / css_output).exists():
                    self.assets.asset_map[css_output] = css_output
        results['asset_map'] = dict(self.assets.asset_map)

    def _write_dev_entrypoint(self) -> None:
        """Create a framework-neutral dev entrypoint from templates/index.html."""
        template = self.root_dir / 'templates' / 'index.html'
        if not template.exists():
            return
        html = template.read_text(encoding='utf-8')
        # Resolve the static URL forms emitted by the Flask, Django, and
        # FastAPI scaffolds. Unknown server-side template syntax is preserved.
        html = re.sub(r"\{\{\s*url_for\(['\"]static['\"],\s*filename=['\"]([^'\"]+)['\"]\)\s*\}\}", r"/static/\1", html)
        html = re.sub(r"\{\%\s*static\s+['\"]([^'\"]+)['\"]\s*\%\}", r"/static/\1", html)
        html = re.sub(r"\{\{\s*url_for\(['\"]static['\"],\s*path=['\"]([^'\"]+)['\"]\)\s*\}\}", r"/static/\1", html)
        for source_name, output_name in sorted(self.assets.asset_map.items(), key=lambda item: len(item[0]), reverse=True):
            html = html.replace(f"/{source_name}", f"/{output_name}")
            html = html.replace(f"'{source_name}'", f"'{output_name}'").replace(f'"{source_name}"', f'"{output_name}"')
        self.writer.write_html(self.out_dir / 'index.html', html)

    def _clean_generated_output(self) -> None:
        """Remove only the explicitly configured generated output directory."""
        root = self.root_dir.resolve()
        output = self.out_dir.resolve()
        if output in {root, root.parent}:
            raise ValueError("Refusing to clean a project root or its parent")
        if output.exists():
            shutil.rmtree(output)
    
    def _compile_file(self, vel_file: Path) -> Dict[str, Any]:
        """Compile a single .vel file."""
        source = vel_file.read_text(encoding='utf-8')
        component_imports = self._resolve_component_imports(vel_file, source)
        compiler_options = dict(self.options)
        compiler_options["component_imports"] = component_imports
        result = Compiler(compiler_options).compile(source, str(vel_file))
        
        if not result['success']:
            raise Exception(result['diagnostics']['errors'])
        
        # Write output
        output_path = self._output_path(vel_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        code = result['code']
        if result.get('map'):
            result['map']['file'] = output_path.name
            result['map']['sources'] = [vel_file.relative_to(self.root_dir).as_posix()]
            code += f"\n//# sourceMappingURL={output_path.name}.map"
        self.writer.write_js(output_path, code)

        if result.get('map'):
            self.writer.write_json(output_path.with_suffix('.js.map'), result['map'])
        
        # Write CSS
        if result.get('css'):
            css_path = output_path.with_suffix('.css')
            self.writer.write_css(css_path, result['css'])
        
        return {
            'output': output_path.relative_to(self.out_dir).as_posix(),
            'size': len(result['code']),
            'result': result,
        }

    def _resolve_component_imports(self, vel_file: Path, source: str) -> Dict[str, str]:
        """Resolve local `.vel` imports to paths in the build output."""
        resolved: Dict[str, str] = {}
        output_path = self._output_path(vel_file)
        pattern = re.compile(r'import\s+([A-Za-z_$][\w$]*)(?:\s*,\s*\{[^}]*\})?\s+from\s+[\'\"]([^\'\"]+\.vel)[\'\"]')
        for match in pattern.finditer(source):
            name, import_path = match.groups()
            if not import_path.startswith('.'):
                continue
            requested = (vel_file.parent / import_path).resolve()
            candidates = [requested]
            if requested.suffix == '':
                candidates.extend([requested.with_suffix('.vel'), requested / 'index.vel'])
            elif requested.suffix != '.vel':
                candidates.append(requested.with_suffix('.vel'))
            child = next((candidate for candidate in candidates if candidate.is_file()), None)
            if child is None:
                raise FileNotFoundError(f"Component import not found: {import_path} in {vel_file}")
            child_output = self._output_path(child)
            specifier = Path(os.path.relpath(child_output, output_path.parent)).as_posix()
            if not specifier.startswith('.'):
                specifier = './' + specifier
            resolved[name] = specifier
        named_pattern = re.compile(r'import\s*\{([^}]+)\}\s*from\s+[\'\"]([^\'\"]+\.vel)[\'\"]')
        for match in named_pattern.finditer(source):
            import_path = match.group(2)
            requested = (vel_file.parent / import_path).resolve()
            candidates = [requested]
            if requested.suffix == '':
                candidates.extend([requested.with_suffix('.vel'), requested / 'index.vel'])
            elif requested.suffix != '.vel':
                candidates.append(requested.with_suffix('.vel'))
            child = next((candidate for candidate in candidates if candidate.is_file()), None)
            if child is None:
                raise FileNotFoundError(f"Component import not found: {import_path} in {vel_file}")
            child_output = self._output_path(child)
            specifier = Path(os.path.relpath(child_output, output_path.parent)).as_posix()
            if not specifier.startswith('.'):
                specifier = './' + specifier
            for item in match.group(1).split(','):
                parts = re.split(r'\s+as\s+', item.strip())
                name = parts[-1].strip()
                if name:
                    resolved[name] = specifier
        return resolved

    def _build_dependency_graph(self, vel_files: List[Path]) -> None:
        """Build a stable graph of relative `.vel` component imports."""
        self.dependency_graph.clear()
        known = {path.resolve(): path.relative_to(self.root_dir).as_posix() for path in vel_files}
        pattern = re.compile(r'import\s+(?:[A-Za-z_$][\w$]*(?:\s*,\s*\{[^}]+\})?|\{[^}]+\}|\*\s+as\s+[A-Za-z_$][\w$]*)\s+from\s+[\'\"]([^\'\"]+)[\'\"]')
        for vel_file in vel_files:
            component = vel_file.relative_to(self.root_dir).as_posix()
            self.dependency_graph.add_component(component)
            source = vel_file.read_text(encoding='utf-8')
            for import_path in pattern.findall(source):
                if not import_path.startswith('.'):
                    continue
                requested = (vel_file.parent / import_path).resolve()
                candidates = [requested]
                if requested.suffix == '':
                    candidates.extend([requested.with_suffix('.vel'), requested / 'index.vel'])
                child = next((candidate for candidate in candidates if candidate in known), None)
                if child is not None:
                    self.dependency_graph.add_dependency(component, known[child])

    def _output_path(self, vel_file: Path) -> Path:
        """Return a stable or content-hashed output path for a component."""
        relative = vel_file.relative_to(self.root_dir)
        if not self.hash_assets:
            return (self.out_dir / relative).with_suffix('.js')
        digest = hashlib.sha256(vel_file.read_bytes()).hexdigest()[:8]
        return self.out_dir / relative.parent / f"{relative.stem}.{digest}.js"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get build statistics."""
        return self.stats
    
    def clean(self) -> None:
        """Clean the build directory."""
        if self.out_dir and self.out_dir.exists():
            import shutil
            shutil.rmtree(self.out_dir)
