"""
Script parser for .vel components.

Parses the <script> section of a .vel file with full JavaScript/TypeScript
support including ES modules, exports, imports, and component options.
"""

import re
import ast
from typing import Optional, Dict, Any, List, Tuple, Set
from dataclasses import dataclass, field

from teloce.sfc.component import ComponentScript
from teloce.javascript.parser import parse_javascript


def _read_ts_balanced(source: str, opening: int, open_char: str = '{', close_char: str = '}') -> int:
    """Return the index after a balanced TS declaration block."""
    depth = 0
    quote = None
    escaped = False
    for index in range(opening, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"`":
            quote = char
        elif char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0:
                return index + 1
    return -1


def _remove_typescript_declarations(source: str) -> str:
    """Remove balanced interface/type declarations without truncating them."""
    pattern = re.compile(r'(?m)^\s*(?:export\s+)?(?:interface|type)\s+[A-Za-z_$][\w$]*(?:\s+extends[^\{=]+)?')
    while True:
        match = pattern.search(source)
        if not match:
            return source
        start = match.start()
        cursor = match.end()
        while cursor < len(source) and source[cursor].isspace():
            cursor += 1
        if cursor < len(source) and source[cursor] == '=':
            cursor += 1
            while cursor < len(source) and source[cursor].isspace():
                cursor += 1
        if cursor < len(source) and source[cursor] == '{':
            end = _read_ts_balanced(source, cursor)
            if end < 0:
                return source
            cursor = end
        else:
            semicolon = source.find(';', cursor)
            cursor = len(source) if semicolon < 0 else semicolon + 1
        source = source[:start] + source[cursor:]


def _transpile_simple_enums(source: str) -> str:
    """Lower simple TypeScript enums to browser JavaScript objects."""
    pattern = re.compile(r'(?m)^(\s*)(export\s+)?enum\s+([A-Za-z_$][\w$]*)\s*\{')
    cursor = 0
    output = []
    while True:
        match = pattern.search(source, cursor)
        if not match:
            output.append(source[cursor:])
            return ''.join(output)
        output.append(source[cursor:match.start()])
        end = _read_ts_balanced(source, match.end() - 1)
        if end < 0:
            output.append(source[match.start():])
            return ''.join(output)
        body = source[match.end():end - 1]
        members = []
        depth = 0
        quote = None
        start = 0
        for index, char in enumerate(body + ','):
            if quote:
                if char == quote and (index == 0 or body[index - 1] != '\\'):
                    quote = None
            elif char in "'\"`":
                quote = char
            elif char in '([{':
                depth += 1
            elif char in ')]}':
                depth -= 1
            elif char == ',' and depth == 0:
                members.append(body[start:index].strip())
                start = index + 1
        values = []
        next_number = 0
        for member in members:
            if not member:
                continue
            if '=' in member:
                name, value = member.split('=', 1)
                name, value = name.strip(), value.strip()
                values.append(f'{name}: {value}')
                if re.fullmatch(r'-?\d+', value):
                    next_number = int(value) + 1
            else:
                name = member.strip()
                values.append(f'{name}: {next_number}')
                next_number += 1
        exported = 'export ' if match.group(2) else ''
        output.append(f'{match.group(1)}{exported}const {match.group(3)} = {{' + ', '.join(values) + '};')
        cursor = end


def strip_typescript_annotations(source: str) -> str:
    """Remove common TS-only syntax while preserving JavaScript expressions."""
    # Type-only imports/declarations have no browser runtime representation.
    source = _transpile_simple_enums(_remove_typescript_declarations(source))
    source = re.sub(r'(?m)^\s*import\s+type\s+[^;]+;?\s*$', '', source)
    source = re.sub(r'(?m)(import\s*\{)\s*type\s+[A-Za-z_$][\w$]*(?:\s+as\s+[A-Za-z_$][\w$]*)?\s*,?', r'\1', source)
    source = re.sub(r'(?m)import\s*\{\s*\}\s*from\s*[\'\"][^\'\"]+[\'\"]\s*;?', '', source)
    source = re.sub(r'(?m)^\s*(?:export\s+)?type\s+[A-Za-z_$][\w$]*\s*=\s*[^;]+;\s*$', '', source)
    source = re.sub(r'\s+as\s+(?:const|readonly)\b', '', source)
    source = re.sub(r'([A-Za-z_$][\w$]*)\s*<[^>{};()]*>\s*(?=\()', r'\1', source)
    # Assertions such as ``value as User``.  Stop before expression syntax.
    source = re.sub(r'\s+as\s+[A-Za-z_$][\w$]*(?:\s*<[^;,)]+>)?(?:\[\])?(?=\s*[,;.)]}])', '', source)
    # Parameter annotations and optional parameter markers.
    source = re.sub(r'([A-Za-z_$][\w$]*)\s*\?\s*:\s*[A-Za-z_$][\w$]*(?:\s*<[^>]*>)?(?:\[\])?(?:\s*\|\s*[A-Za-z_$][\w$]*)*', r'\1', source)
    source = re.sub(r'([A-Za-z_$][\w$]*)\s*:\s*[A-Za-z_$][\w$]*(?:\s*<[^>]*>)?(?:\[\])?(?:\s*\|\s*[A-Za-z_$][\w$]*)*(?=\s*[,)=])', r'\1', source)
    # Function return annotations: ``): Promise<T> {`` / ``): void =>``.
    source = re.sub(r'\)\s*:\s*[A-Za-z_$][\w$]*(?:\s*<[^>]*>)?(?:\[\])?(?:\s*\|\s*[A-Za-z_$][\w$]*)*(?=\s*[{=])', ')', source)
    source = re.sub(r'\)\s*:\s*\{[^{}]*\}\s*(?=\{)', ')', source)
    # Variable annotations in the common ``const value: Type =`` form.
    source = re.sub(r'([A-Za-z_$][\w$]*)\s*:\s*[A-Za-z_$][\w$]*(?:\[\])?(?=\s*=)', r'\1', source)
    return source


@dataclass
class ScriptImport:
    """Represents an import statement."""
    source: str
    names: List[str]
    is_default: bool = False
    is_namespace: bool = False
    alias: Optional[str] = None
    line: int = 0


@dataclass
class ScriptExport:
    """Represents an export statement."""
    name: str
    local_name: Optional[str] = None
    is_default: bool = False
    is_type: bool = False
    line: int = 0


@dataclass
class ScriptMethod:
    """Represents a method in the component."""
    name: str
    body: str
    params: List[str]
    is_async: bool = False
    line: int = 0


@dataclass
class ScriptComputed:
    """Represents a computed property in the component."""
    name: str
    body: str
    line: int = 0


@dataclass
class ScriptProp:
    """Represents a prop definition."""
    name: str
    type: Optional[str] = None
    required: bool = False
    default: Optional[str] = None
    validator: Optional[str] = None
    line: int = 0


@dataclass
class ScriptLifecycle:
    """Represents a lifecycle hook."""
    name: str
    body: str
    line: int = 0


class ScriptParser:
    """
    Parses the script section of a .vel component with full JavaScript support.
    """
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.imports: List[ScriptImport] = []
        self.exports: List[ScriptExport] = []
        self.components: Dict[str, str] = {}  # Component name -> import source
        self._method_params: Dict[str, str] = {}
        self._method_async: Dict[str, bool] = {}
    
    def parse(self, source: str, filename: str = "<input>") -> ComponentScript:
        """
        Parse the script section into a ComponentScript object.
        
        Args:
            source: The script source code
            filename: The source filename
            
        Returns:
            A ComponentScript object.
        """
        self.errors = []
        self.warnings = []
        self.imports = []
        self.exports = []
        self.components = {}
        self._method_params = {}
        self._method_async = {}
        
        original_source = source
        if str(self.options.get("lang", "js")).lower() in {"ts", "tsx", "typescript"}:
            source = strip_typescript_annotations(source)
        script = ComponentScript(raw=original_source)
        script.module_code = self._extract_module_code(source)
        
        if not source or not source.strip():
            self.warnings.append("Empty script section")
            return script
        
        try:
            # Validate module structure with Teloce's source-located parser
            # before extracting component options. The original source is
            # preserved for generation; this pass only establishes safe
            # statement boundaries and catches malformed delimiters.
            parse_javascript(source)
            # Parse imports
            self._parse_imports(source)
            script.imports = list(self.imports)
            
            # Parse exports
            self._parse_exports(source)
            
            # Extract component options
            script.name = self._extract_component_name(source)
            script.data = self._extract_data(source)
            script.methods = self._extract_methods(source)
            script.method_params = dict(self._method_params)
            script.method_async = dict(self._method_async)
            script.computed = self._extract_computed(source)
            script.props = self._extract_props(source)
            script.lifecycle = self._extract_lifecycle(source)
            
            # Extract registered components
            self._extract_components(source)
            
            # Extract watch and other options
            script.watch = self._extract_watch(source)
            script.emits = self._extract_emits(source)
            
        except Exception as e:
            self.errors.append(f"Error parsing script: {str(e)}")
        
        return script

    def _extract_module_code(self, source: str) -> str:
        """Preserve executable module-level code around the component export."""
        code = source
        default_match = re.search(r'\bexport\s+default\s+', code)
        if default_match:
            start = default_match.start()
            cursor = default_match.end()
            while cursor < len(code) and code[cursor].isspace():
                cursor += 1
            if cursor < len(code) and code[cursor] == '{':
                block = self._read_balanced_pair(code, cursor, '{', '}')
                if block:
                    end = cursor + len(block)
                    while end < len(code) and code[end] in ' ;\t\r\n':
                        end += 1
                    code = code[:start] + code[end:]
        # Local component imports are re-emitted with resolved build URLs by
        # the generator; package imports and ordinary module code remain.
        code = re.sub(
            r'(?m)^\s*import\s+(?:[^\n;]+)\s+from\s+[\'\"]([^\'\"]+\.vel)[\'\"]\s*;?\s*$',
            '', code,
        )
        code = re.sub(r'(?m)^\s*import\s+[\'\"]([^\'\"]+\.vel)[\'\"]\s*;?\s*$', '', code)
        return code.strip()
    
    def _parse_imports(self, source: str):
        """Parse imports from source-preserving AST nodes."""
        for node in parse_javascript(source).body:
            if node.kind != "ImportDeclaration":
                continue
            statement = node.source.strip().rstrip(";").strip()
            line = node.line
            side_effect = re.fullmatch(r'import\s*([\'"])(.*?)\1', statement, re.S)
            if side_effect:
                self.imports.append(ScriptImport(side_effect.group(2), [], line=line))
                continue
            match = re.fullmatch(r'import\s+(.+?)\s+from\s+([\'"])(.*?)\2', statement, re.S)
            if not match:
                raise ValueError(f"Invalid import declaration: {statement}")
            bindings, source_path = match.group(1).strip(), match.group(3)
            default_name = None
            if bindings.startswith("*"):
                namespace = re.fullmatch(r'\*\s+as\s+([A-Za-z_$][\w$]*)', bindings)
                if not namespace:
                    raise ValueError(f"Invalid namespace import: {statement}")
                self.imports.append(ScriptImport(source_path, ["*"], is_namespace=True, alias=namespace.group(1), line=line))
                continue
            if bindings.startswith("{"):
                named = bindings
            else:
                default_name, _, named = bindings.partition(",")
                default_name = default_name.strip()
                if not re.fullmatch(r'[A-Za-z_$][\w$]*', default_name):
                    raise ValueError(f"Invalid default import: {statement}")
                self.imports.append(ScriptImport(source_path, [default_name], is_default=True, line=line))
                if default_name[0].isupper():
                    self.components[default_name] = source_path
            if named.strip():
                if not (named.strip().startswith("{") and named.strip().endswith("}")):
                    raise ValueError(f"Invalid named import: {statement}")
                for part in named.strip()[1:-1].split(","):
                    part = part.strip()
                    if not part:
                        continue
                    pieces = re.split(r'\s+as\s+', part)
                    imported = pieces[0].strip()
                    alias = pieces[-1].strip() if len(pieces) > 1 else None
                    self.imports.append(ScriptImport(source_path, [imported], alias=alias, line=line))
    
    def _parse_exports(self, source: str):
        """Parse export statements."""
        # Default export: export default { ... }
        default_match = re.search(r'export\s+default\s+({[\s\S]*?})(?=\n\s*\n|\s*$)', source)
        if default_match:
            self.exports.append(ScriptExport('default', is_default=True, line=source[:default_match.start()].count('\n') + 1))
        
        # Named export: export const X = ...
        named_pattern = r'export\s+(?:const|let|var|function|class)\s+(\w+)'
        for match in re.finditer(named_pattern, source):
            name = match.group(1)
            self.exports.append(ScriptExport(name, line=source[:match.start()].count('\n') + 1))
        
        # Export list: export { X, Y }
        export_list_pattern = r'export\s*{([^}]+)}'
        for match in re.finditer(export_list_pattern, source):
            names_str = match.group(1)
            for name_part in names_str.split(','):
                name_part = name_part.strip()
                if ' as ' in name_part:
                    local, exported = name_part.split(' as ')
                    self.exports.append(ScriptExport(exported.strip(), local_name=local.strip(), line=source[:match.start()].count('\n') + 1))
                else:
                    name = name_part.strip()
                    if name:
                        self.exports.append(ScriptExport(name, line=source[:match.start()].count('\n') + 1))
    
    def _extract_component_name(self, source: str) -> Optional[str]:
        """Extract component name from the script."""
        # Check for name in export default object
        name_pattern = r'name\s*:\s*["\']([^"\']+)["\']'
        match = re.search(name_pattern, source)
        if match:
            return match.group(1)
        
        # Check for name in exported const
        const_pattern = r'export\s+const\s+(\w+)\s*=\s*{'
        match = re.search(const_pattern, source)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_data(self, source: str) -> Optional[str]:
        """Extract data function from the script."""
        # data() { return { ... } }
        match = re.search(r'data\s*\(\s*\)\s*{\s*return\s*{', source)
        if match:
            opening = source.find('{', match.start() + match.group(0).rfind('return'))
            value = self._read_balanced(source, opening)
            if value is not None:
                return value.strip()
        
        # data: () => ({ ... }) / data: () => ({ nested: { ... } })
        arrow_match = re.search(r'data\s*:\s*\(\)\s*=>\s*', source)
        if arrow_match:
            start = arrow_match.end()
            while start < len(source) and source[start].isspace():
                start += 1
            if start < len(source) and source[start] == '(':
                wrapped = self._read_balanced_pair(source, start, '(', ')')
                if wrapped:
                    value = wrapped[1:-1].strip()
                    if value.startswith('{'):
                        object_value = self._read_balanced_pair(value, 0, '{', '}')
                        if object_value:
                            return object_value.strip()
            elif start < len(source) and source[start] == '{':
                value = self._read_balanced_pair(source, start, '{', '}')
                if value:
                    return value.strip()
        
        return None

    def _read_balanced(self, source: str, opening: int) -> Optional[str]:
        """Read a balanced JavaScript brace expression."""
        if opening < 0 or opening >= len(source) or source[opening] != '{':
            return None
        depth = 0
        quote = None
        escaped = False
        for index in range(opening, len(source)):
            char = source[index]
            if quote:
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == quote:
                    quote = None
                continue
            if char in "'\"`":
                quote = char
            elif char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    return source[opening:index + 1]
        return None
    
    def _extract_methods(self, source: str) -> Dict[str, str]:
        """Extract methods from the script."""
        methods = {}
        self._method_params = {}
        self._method_async = {}
        
        # Find methods block
        methods_block = self._extract_block(source, 'methods')
        if methods_block:
            # Scan balanced parameter/body pairs so nested functions and
            # braces inside strings do not truncate a method.
            cursor = 0
            while cursor < len(methods_block):
                match = re.search(r'(?:async\s+)?([A-Za-z_$][\w$]*)\s*\(', methods_block[cursor:])
                if not match:
                    break
                name = match.group(1)
                open_paren = cursor + match.end() - 1
                params_block = self._read_balanced_pair(methods_block, open_paren, '(', ')')
                if not params_block:
                    break
                after_params = open_paren + len(params_block)
                brace = methods_block.find('{', after_params)
                if brace < 0:
                    break
                body_block = self._read_balanced_pair(methods_block, brace, '{', '}')
                if not body_block:
                    break
                params = params_block[1:-1].strip()
                body = body_block[1:-1].strip()
                if name and body:
                    methods[name] = body
                    self._method_params[name] = params
                    self._method_async[name] = re.match(r"async\s+", match.group(0)) is not None
                cursor = brace + len(body_block)
        
        # Also check for methods outside explicit block
        # This handles Vue 3 Composition API style
        function_pattern = r'(?:async\s+)?(\w+)\s*\(\s*([^)]*)\s*\)\s*{\s*([\s\S]*?)\s*}\s*,?'
        for match in re.finditer(function_pattern, source):
            # Skip if inside another block
            context = source[:match.start()]
            if self._is_inside_block(context, ['methods', 'computed', 'props', 'watch']):
                continue
            name = match.group(1)
            # Skip lifecycle hooks
            if name in ['data', 'computed', 'watch', 'beforeMount', 'mounted', 'beforeUpdate', 'updated', 
                        'beforeUnmount', 'unmounted', 'beforeCreate', 'created']:
                continue
            params = match.group(2).strip()
            body = match.group(3).strip()
            if name and body and name not in methods:
                methods[name] = body
                self._method_params[name] = params
                self._method_async[name] = match.group(0).lstrip().startswith("async ")
        
        return methods

    def _read_balanced_pair(self, source: str, opening: int, open_char: str, close_char: str) -> Optional[str]:
        """Read a balanced JS pair while respecting quoted strings/comments."""
        if opening < 0 or opening >= len(source) or source[opening] != open_char:
            return None
        depth = 0
        quote = None
        escaped = False
        i = opening
        while i < len(source):
            char = source[i]
            if quote:
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == quote:
                    quote = None
                i += 1
                continue
            if char in "'\"`":
                quote = char
            elif char == '/' and i + 1 < len(source) and source[i + 1] == '/':
                newline = source.find('\n', i + 2)
                i = len(source) if newline < 0 else newline
                continue
            elif char == '/' and i + 1 < len(source) and source[i + 1] == '*':
                end = source.find('*/', i + 2)
                i = len(source) if end < 0 else end + 2
                continue
            elif char == open_char:
                depth += 1
            elif char == close_char:
                depth -= 1
                if depth == 0:
                    return source[opening:i + 1]
            i += 1
        return None
    
    def _extract_computed(self, source: str) -> Dict[str, str]:
        """Extract computed properties from the script."""
        computed = {}
        
        # Find computed block
        computed_block = self._extract_block(source, 'computed')
        if computed_block:
            cursor = 0
            while cursor < len(computed_block):
                match = re.search(r'([A-Za-z_$][\w$]*)\s*\(\s*\)\s*\{', computed_block[cursor:])
                if not match:
                    break
                name = match.group(1)
                brace = cursor + match.end() - 1
                body_block = self._read_balanced_pair(computed_block, brace, '{', '}')
                if not body_block:
                    break
                body = body_block[1:-1].strip()
                if name and body:
                    computed[name] = body
                cursor = brace + len(body_block)
            
            # Arrow function computed: name: () => value
            arrow_pattern = r'(\w+)\s*:\s*\(\)\s*=>\s*([^,\n]+)\s*,?'
            for match in re.finditer(arrow_pattern, computed_block):
                name = match.group(1)
                body = f"return {match.group(2).strip()}"
                if name and body and name not in computed:
                    computed[name] = body
        
        # Check for getters in computed
        getter_pattern = r'(\w+)\s*:\s*{\s*get\s*\(\s*\)\s*{\s*([\s\S]*?)\s*}\s*}'
        for match in re.finditer(getter_pattern, source):
            name = match.group(1)
            body = match.group(2).strip()
            if name and body and name not in computed:
                computed[name] = body
        
        return computed
    
    def _extract_props(self, source: str) -> Dict[str, Dict[str, Any]]:
        """Extract props from the script."""
        props = {}
        
        # Find props block
        props_block = self._extract_block(source, 'props')
        if props_block:
            # Parse array props: ['prop1', 'prop2']
            array_match = re.search(r'\[\s*([\s\S]*?)\s*\]', props_block)
            if array_match:
                prop_names = re.findall(r'["\']([^"\']+)["\']', array_match.group(1))
                for name in prop_names:
                    props[name] = {'type': None, 'required': False, 'default': None}
            
            # Parse object props: { prop: { type: String, required: true } }
            if props_block.strip().startswith('{') and props_block.strip().endswith('}'):
                prop_str = props_block.strip()[1:-1]
                # Parse each prop definition
                prop_defs = self._parse_prop_definitions(prop_str)
                props.update(prop_defs)
        
        return props
    
    def _parse_prop_definitions(self, prop_str: str) -> Dict[str, Dict[str, Any]]:
        """Parse prop definitions from a string."""
        props = {}
        i = 0
        while i < len(prop_str):
            # Skip whitespace
            while i < len(prop_str) and prop_str[i].isspace():
                i += 1
            
            if i >= len(prop_str):
                break
            
            # Read property name
            name_start = i
            while i < len(prop_str) and (prop_str[i].isalnum() or prop_str[i] in '_\'""'):
                i += 1
            name = prop_str[name_start:i].strip()
            name = name.strip("'\"")
            
            if not name:
                break
            
            # Skip to colon
            while i < len(prop_str) and prop_str[i] != ':':
                i += 1
            if i >= len(prop_str):
                break
            i += 1  # Skip ':'
            
            # Parse prop definition
            prop_def = self._parse_prop_definition(prop_str, i)
            if prop_def:
                props[name] = prop_def[0]
                i = prop_def[1]
            
            # Skip comma
            while i < len(prop_str) and prop_str[i] != ',':
                i += 1
            if i < len(prop_str) and prop_str[i] == ',':
                i += 1
        
        return props
    
    def _parse_prop_definition(self, prop_str: str, start: int) -> Tuple[Dict[str, Any], int]:
        """Parse a single prop definition."""
        i = start
        
        # Skip whitespace
        while i < len(prop_str) and prop_str[i].isspace():
            i += 1
        
        if i >= len(prop_str):
            return {}, i
        
        prop_def = {'type': None, 'required': False, 'default': None, 'validator': None}
        
        # Check if it's a type literal (String, Number, etc.)
        if i < len(prop_str) and prop_str[i].isalpha():
            type_start = i
            while i < len(prop_str) and (prop_str[i].isalnum() or prop_str[i] == '_'):
                i += 1
            type_name = prop_str[type_start:i]
            if type_name in ['String', 'Number', 'Boolean', 'Array', 'Object', 'Function', 'Symbol']:
                prop_def['type'] = type_name
                return prop_def, i
        
        # Check for object definition: { type: String, required: true }
        if i < len(prop_str) and prop_str[i] == '{':
            i += 1  # Skip '{'
            
            while i < len(prop_str):
                # Skip whitespace
                while i < len(prop_str) and prop_str[i].isspace():
                    i += 1
                
                if i >= len(prop_str) or prop_str[i] == '}':
                    break
                
                # Read key
                key_start = i
                while i < len(prop_str) and (prop_str[i].isalnum() or prop_str[i] == '_'):
                    i += 1
                key = prop_str[key_start:i]
                
                # Skip to colon
                while i < len(prop_str) and prop_str[i] != ':':
                    i += 1
                if i >= len(prop_str):
                    break
                i += 1  # Skip ':'
                
                # Skip whitespace
                while i < len(prop_str) and prop_str[i].isspace():
                    i += 1
                
                if i >= len(prop_str):
                    break
                
                # Parse value
                if key == 'type':
                    # Parse type
                    if prop_str[i] == '[':
                        # Array of types
                        i += 1
                        types = []
                        while i < len(prop_str) and prop_str[i] != ']':
                            type_start = i
                            while i < len(prop_str) and (prop_str[i].isalnum() or prop_str[i] == '_'):
                                i += 1
                            type_name = prop_str[type_start:i].strip()
                            if type_name:
                                types.append(type_name)
                            while i < len(prop_str) and prop_str[i] in ' ,':
                                i += 1
                        if i < len(prop_str) and prop_str[i] == ']':
                            i += 1
                        prop_def['type'] = '|'.join(types) if types else None
                    else:
                        type_start = i
                        while i < len(prop_str) and (prop_str[i].isalnum() or prop_str[i] == '_'):
                            i += 1
                        type_name = prop_str[type_start:i].strip()
                        if type_name:
                            prop_def['type'] = type_name
                elif key == 'required':
                    # Parse boolean
                    if prop_str[i:i+4] == 'true':
                        prop_def['required'] = True
                        i += 4
                    elif prop_str[i:i+5] == 'false':
                        prop_def['required'] = False
                        i += 5
                elif key == 'default':
                    # Parse default
                    default_start = i
                    if prop_str[i] == '(':
                        # Function default
                        i += 1
                        parens = 1
                        while i < len(prop_str) and parens > 0:
                            if prop_str[i] == '(':
                                parens += 1
                            elif prop_str[i] == ')':
                                parens -= 1
                            i += 1
                        prop_def['default'] = prop_str[default_start:i]
                    else:
                        while i < len(prop_str) and prop_str[i] not in '},':
                            i += 1
                        prop_def['default'] = prop_str[default_start:i].strip()
                elif key == 'validator':
                    # Preserve the complete function/arrow expression.
                    validator_start = i
                    depth = 0
                    quote = None
                    escaped = False
                    while i < len(prop_str):
                        char = prop_str[i]
                        if quote:
                            if escaped:
                                escaped = False
                            elif char == '\\':
                                escaped = True
                            elif char == quote:
                                quote = None
                        elif char in "'\"`":
                            quote = char
                        elif char in '([{':
                            depth += 1
                        elif char in ')]}':
                            if depth == 0:
                                break
                            depth -= 1
                        elif char == ',' and depth == 0:
                            break
                        i += 1
                    prop_def['validator'] = prop_str[validator_start:i].strip()
                
                # Skip to comma or end
                while i < len(prop_str) and prop_str[i] not in ',}':
                    i += 1
                if i < len(prop_str) and prop_str[i] == ',':
                    i += 1
            
            if i < len(prop_str) and prop_str[i] == '}':
                i += 1
        
        return prop_def, i
    
    def _extract_lifecycle(self, source: str) -> Dict[str, str]:
        """Extract lifecycle hooks from the script."""
        lifecycle = {}
        
        lifecycle_hooks = [
            'beforeMount', 'mounted', 'beforeUpdate', 'updated',
            'beforeUnmount', 'unmounted', 'beforeCreate', 'created',
            'activated', 'deactivated', 'errorCaptured'
        ]
        
        for hook in lifecycle_hooks:
            match = re.search(rf'{hook}\s*\(\s*\)\s*\{{', source)
            if match:
                brace = source.find('{', match.start(), match.end())
                block = self._read_balanced_pair(source, brace, '{', '}')
                body = block[1:-1].strip() if block else ""
                if body:
                    lifecycle[hook] = body
        
        return lifecycle
    
    def _extract_watch(self, source: str) -> Dict[str, str]:
        """Extract watch properties from the script."""
        watch = {}
        
        watch_block = self._extract_block(source, 'watch')
        if watch_block:
            # Parse watch entries
            watch_pattern = r'(\w+)\s*:\s*{\s*handler\s*\(\s*([^)]*)\s*\)\s*{\s*([\s\S]*?)\s*}\s*}'
            for match in re.finditer(watch_pattern, watch_block):
                prop = match.group(1)
                params = match.group(2).strip()
                body = match.group(3).strip()
                if prop and body:
                    watch[prop] = body
            
            # Simple watch: prop: function(newVal, oldVal) { ... }
            simple_pattern = r'(\w+)\s*:\s*function\s*\(\s*([^)]*)\s*\)\s*{\s*([\s\S]*?)\s*}'
            for match in re.finditer(simple_pattern, watch_block):
                prop = match.group(1)
                params = match.group(2).strip()
                body = match.group(3).strip()
                if prop and body and prop not in watch:
                    watch[prop] = body
        
        return watch
    
    def _extract_emits(self, source: str) -> List[str]:
        """Extract emits from the script."""
        emits = []
        
        # Find emits block
        emits_block = self._extract_block(source, 'emits')
        if emits_block:
            # Array emits: ['event1', 'event2']
            array_match = re.search(r'\[\s*([\s\S]*?)\s*\]', emits_block)
            if array_match:
                event_names = re.findall(r'["\']([^"\']+)["\']', array_match.group(1))
                emits.extend(event_names)
        
        return emits
    
    def _extract_components(self, source: str):
        """Extract component registrations from the script."""
        # Find components block
        comp_block = self._extract_block(source, 'components')
        if comp_block:
            # Parse component registrations
            comp_pattern = r'(\w+)\s*:\s*(\w+)'
            for match in re.finditer(comp_pattern, comp_block):
                local_name = match.group(1)
                import_name = match.group(2)
                # Check if the import is in our imports
                for imp in self.imports:
                    if import_name in imp.names or imp.alias == import_name:
                        self.components[local_name] = imp.source
                        break
    
    def _extract_block(self, source: str, block_name: str) -> Optional[str]:
        """Extract a named block from the source."""
        start_match = self._find_property(source, block_name)
        if start_match is None:
            return None

        start = start_match

        # Find the block content
        while start < len(source) and source[start].isspace():
            start += 1
        if start >= len(source):
            return None
        
        # Check if it's an object or array
        char = source[start]
        if char == '{':
            # Object block
            return self._extract_object_block(source, start)
        elif char == '[':
            # Array block
            return self._extract_array_block(source, start)
        
        return None

    @staticmethod
    def _find_property(source: str, name: str) -> Optional[int]:
        """Find a top-level-looking ``name:`` outside JS strings/comments.

        Option extraction is intentionally lightweight, but it must not let
        documentation strings such as ``"computed: { fake: true }"`` become
        component options. This scanner only identifies the property; the
        existing balanced readers still parse its value.
        """
        quote = None
        escaped = False
        line_comment = block_comment = False
        index = 0
        while index < len(source):
            char = source[index]
            nxt = source[index + 1] if index + 1 < len(source) else ""
            if line_comment:
                if char == "\n": line_comment = False
            elif block_comment:
                if char == "*" and nxt == "/": block_comment = False; index += 1
            elif quote:
                if escaped: escaped = False
                elif char == "\\": escaped = True
                elif char == quote: quote = None
            elif char in "'\"`": quote = char
            elif char == "/" and nxt == "/": line_comment = True; index += 1
            elif char == "/" and nxt == "*": block_comment = True; index += 1
            elif source.startswith(name, index):
                before = source[index - 1] if index else ""
                after_index = index + len(name)
                if (not (before.isalnum() or before in "_$") and
                        (after_index == len(source) or not (source[after_index].isalnum() or source[after_index] in "_$"))):
                    cursor = after_index
                    while cursor < len(source) and source[cursor].isspace(): cursor += 1
                    if cursor < len(source) and source[cursor] == ":":
                        return cursor + 1
            index += 1
        return None
    
    def _extract_object_block(self, source: str, start: int) -> Optional[str]:
        """Extract an object block from the source."""
        if start >= len(source) or source[start] != '{':
            return None
        
        i = start + 1
        braces = 1
        in_string = False
        in_regex = False
        escape = False
        
        while i < len(source) and braces > 0:
            char = source[i]
            
            if escape:
                escape = False
                i += 1
                continue
            
            if char == '\\':
                escape = True
                i += 1
                continue
            
            if in_string:
                if char == in_string:
                    in_string = False
                i += 1
                continue
            
            if char == '"' or char == "'":
                in_string = char
                i += 1
                continue
            
            if char == '/':
                # Check for regex
                if i + 1 < len(source) and source[i + 1] == '/':
                    in_regex = True
                    i += 2
                    continue
                if in_regex and char == '/':
                    in_regex = False
                    i += 1
                    continue
            
            if char == '{':
                braces += 1
            elif char == '}':
                braces -= 1
            
            i += 1
        
        if braces == 0:
            return source[start:i]
        
        return None
    
    def _extract_array_block(self, source: str, start: int) -> Optional[str]:
        """Extract an array block from the source."""
        if start >= len(source) or source[start] != '[':
            return None
        
        i = start + 1
        braces = 1
        in_string = False
        escape = False
        
        while i < len(source) and braces > 0:
            char = source[i]
            
            if escape:
                escape = False
                i += 1
                continue
            
            if char == '\\':
                escape = True
                i += 1
                continue
            
            if in_string:
                if char == in_string:
                    in_string = False
                i += 1
                continue
            
            if char == '"' or char == "'":
                in_string = char
                i += 1
                continue
            
            if char == '[':
                braces += 1
            elif char == ']':
                braces -= 1
            
            i += 1
        
        if braces == 0:
            return source[start:i]
        
        return None
    
    def _is_inside_block(self, context: str, block_names: List[str]) -> bool:
        """Check if we're inside a specific block."""
        for block in block_names:
            pattern = rf'{block}\s*:'
            match = re.search(pattern, context)
            if match:
                # Check if the block is closed
                block_start = match.end()
                if block_start < len(context):
                    # Find the matching closing brace
                    return True
        return False
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
