"""
JavaScript generator.

Generates JavaScript code from the AST.
"""

from typing import List, Optional, Any
import json
import html
import re
from teloce.ast.elements import ElementFactory
from teloce.css.hashing import HashGenerator
from teloce.css.modules import CSSModules

from teloce.ast.nodes import ASTNode, ElementNode, TextNode, InterpolationNode, ForNode, IfNode
from teloce.sfc.component import Component


SAFE_EXPRESSION_RUNTIME = r'''
const __tokenize = source => {
  const tokens = []; let index = 0; const text = String(source || "");
  const operators = ["===", "!==", ">=", "<=", "&&", "||", "??", "==", "!=", "=>", "?."];
  while (index < text.length) {
    const current = text[index];
    if (/\s/.test(current)) { index += 1; continue; }
    if (current === "'" || current === '"') {
      const quote = current; index += 1; let value = "";
      while (index < text.length && text[index] !== quote) {
        if (text[index] === "\\" && index + 1 < text.length) { const next = text[index + 1]; value += ({ n: "\n", r: "\r", t: "\t" }[next] ?? next); index += 2; }
        else { value += text[index]; index += 1; }
      }
      index += 1; tokens.push({ type: "literal", value }); continue;
    }
    const number = text.slice(index).match(/^(?:\d+(?:\.\d*)?|\.\d+)/);
    if (number) { tokens.push({ type: "literal", value: Number(number[0]) }); index += number[0].length; continue; }
    const identifier = text.slice(index).match(/^[A-Za-z_$][\w$]*/);
    if (identifier) { tokens.push({ type: "identifier", value: identifier[0] }); index += identifier[0].length; continue; }
    const operator = operators.find(value => text.startsWith(value, index));
    if (operator) { tokens.push({ type: "operator", value: operator }); index += operator.length; continue; }
    tokens.push({ type: "operator", value: current }); index += 1;
  }
  tokens.push({ type: "eof", value: "" }); return tokens;
};
const __safeEvaluate = (expression, scope) => {
  const tokens = __tokenize(expression); let cursor = 0;
  const peek = () => tokens[cursor]; const take = value => { if (!value || peek().value === value) return tokens[cursor++]; return null; };
  const lookup = name => {
    if (name === "true") return true; if (name === "false") return false; if (name === "null") return null; if (name === "undefined") return undefined;
    const builtins = { Math, Number, String, Boolean, Array, Object, JSON, Date, parseInt, parseFloat, isNaN, window: typeof window === "undefined" ? undefined : window, document: typeof document === "undefined" ? undefined : document };
    if (Object.prototype.hasOwnProperty.call(scope || {}, name)) return scope[name];
    return builtins[name];
  };
  const precedence = { "||": 1, "??": 1, "&&": 2, "==": 3, "!=": 3, "===": 3, "!==": 3, "<": 4, ">": 4, "<=": 4, ">=": 4, "+": 5, "-": 5, "*": 6, "/": 6, "%": 6 };
  const primary = () => {
    const token = take();
    if (token.type === "literal") return token.value;
    if (token.type === "identifier") return lookup(token.value);
    if (token.value === "(") { const value = expressionParser(0); take(")"); return value; }
    if (token.value === "[") { const values = []; while (peek().value !== "]" && peek().type !== "eof") { values.push(expressionParser(0)); if (!take(",")) break; } take("]"); return values; }
    if (token.value === "{") { const result = {}; while (peek().value !== "}" && peek().type !== "eof") { const key = take(); const name = key.value; if (take(":")) result[name] = expressionParser(0); else result[name] = lookup(name); if (!take(",")) break; } take("}"); return result; }
    return undefined;
  };
  const postfix = () => {
    let value = primary(); let owner = null;
    while (true) {
      if (take(".") || take("?.")) { owner = value; const property = take(); value = value == null ? undefined : value[property.value]; continue; }
      if (take("[")) { owner = value; const property = expressionParser(0); take("]"); value = value == null ? undefined : value[property]; continue; }
      if (take("(")) { const args = []; while (peek().value !== ")" && peek().type !== "eof") { args.push(expressionParser(0)); if (!take(",")) break; } take(")"); if (typeof value === "function") value = value.apply(owner || scope, args); owner = null; continue; }
      break;
    }
    return value;
  };
  const unary = () => { if (take("!")) return !unary(); if (take("-")) return -unary(); if (take("+")) return +unary(); if (peek().value === "typeof") { take(); return typeof unary(); } return postfix(); };
  const apply = (operator, left, right) => { if (operator === "||") return left || right; if (operator === "&&") return left && right; if (operator === "??") return left ?? right; if (operator === "===") return left === right; if (operator === "!==") return left !== right; if (operator === "==") return left == right; if (operator === "!=") return left != right; if (operator === "<") return left < right; if (operator === ">") return left > right; if (operator === "<=") return left <= right; if (operator === ">=") return left >= right; if (operator === "+") return left + right; if (operator === "-") return left - right; if (operator === "*") return left * right; if (operator === "/") return left / right; if (operator === "%") return left % right; return left; };
  const expressionParser = minimum => { let left = unary(); while (precedence[peek().value] >= minimum) { const operator = take().value; const right = expressionParser(precedence[operator] + 1); left = apply(operator, left, right); } if (minimum === 0 && take("?")) { const yes = expressionParser(0); take(":"); const no = expressionParser(0); left = left ? yes : no; } return left; };
  return expressionParser(0);
};
const __splitEventStatements = source => { const result = []; let start = 0; let depth = 0; let quote = ""; let escaped = false; for (let index = 0; index < String(source).length; index += 1) { const character = String(source)[index]; if (quote) { if (escaped) escaped = false; else if (character === "\\") escaped = true; else if (character === quote) quote = ""; continue; } if (character === "\"" || character === "'") { quote = character; continue; } if ("([{".includes(character)) depth += 1; else if (")]}".includes(character)) depth -= 1; else if (character === "," && depth === 0) { result.push(String(source).slice(start, index).trim()); start = index + 1; } } result.push(String(source).slice(start).trim()); return result.filter(Boolean); };
const __setSafePath = (expression, value, scope) => { const path = String(expression).trim().split(".").filter(Boolean); if (!path.length) return value; if (path.length === 1) scope[path[0]] = value; else { let target = scope[path[0]]; for (const part of path.slice(1, -1)) target = target?.[part]; if (target != null) target[path[path.length - 1]] = value; } return value; };
const __runEventExpression = (expression, scope) => { let result; for (const statement of __splitEventStatements(expression)) { const update = statement.match(/^(.+?)\s*(\+\+|--)$/); if (update) { const current = __safeEvaluate(update[1], scope); result = __setSafePath(update[1], Number(current || 0) + (update[2] === "++" ? 1 : -1), scope); continue; } const assignment = statement.match(/^(.+?)\s*(\+=|-=|\*=|\/=|=)\s*(.+)$/); if (assignment) { const current = __safeEvaluate(assignment[1], scope); const next = __safeEvaluate(assignment[3], scope); const value = assignment[2] === "=" ? next : assignment[2] === "+=" ? current + next : assignment[2] === "-=" ? current - next : assignment[2] === "*=" ? current * next : current / next; result = __setSafePath(assignment[1], value, scope); continue; } result = __safeEvaluate(statement, scope); } return result; };
'''


class Generator:
    """
    Generates JavaScript code from the AST.
    """
    
    def __init__(self, options: Optional[dict] = None):
        self.options = options or {}
        self.dev = self.options.get("dev", True)
        self.minify = self.options.get("minify", False)
        self.indent_level = 0
        self.scope_id = None
        self.module_mapping = {}
    
    def generate(self, nodes: List[ASTNode], component: Component) -> str:
        """Generate JavaScript code."""
        self.indent_level = 0
        self.scope_id = HashGenerator().generate_scope_id(component.name) if component.style.scoped else None
        all_style_css = "\n".join(style.css for style in getattr(component, "styles", []) or [component.style])
        self.module_mapping = CSSModules.mapping(all_style_css, component.name) if component.style.module else {}
        
        lines = []
        
        # Add import statements
        lines.append('// Generated by Teloce-Py')
        lines.extend(self._generate_component_imports(component))
        module_code = getattr(component.script, "module_code", "")
        if module_code:
            lines.append(module_code)
        lines.append('')
        
        # Generate component code
        lines.append('const __component = {')
        self.indent_level += 1
        
        # Name
        lines.append(f'{self._indent()}name: "{component.name}",')
        lines.append('')
        
        # Data
        if component.script_data:
            lines.append(f'{self._indent()}data() {{')
            self.indent_level += 1
            lines.append(f'{self._indent()}return {component.script_data};')
            self.indent_level -= 1
            lines.append(f'{self._indent()}}},')
            lines.append('')
        
        # Methods
        if component.script_methods:
            lines.append(f'{self._indent()}methods: {{')
            self.indent_level += 1
            for method_name, method_code in component.script_methods.items():
                params = getattr(component.script, "method_params", {}).get(method_name, "")
                prefix = "async " if getattr(component.script, "method_async", {}).get(method_name, False) else ""
                lines.append(f'{self._indent()}{prefix}{method_name}({params}) {{')
                self.indent_level += 1
                for line in method_code.split('\n'):
                    if line.strip():
                        lines.append(f'{self._indent()}{line}')
                self.indent_level -= 1
                lines.append(f'{self._indent()}}},')
            self.indent_level -= 1
            lines.append(f'{self._indent()}}},')
            lines.append('')

        if component.script.props:
            lines.append(f'{self._indent()}props: {json.dumps(component.script.props)},')
            lines.append('')
        
        # Computed
        if component.script_computed:
            lines.append(f'{self._indent()}computed: {{')
            self.indent_level += 1
            for comp_name, comp_code in component.script_computed.items():
                lines.append(f'{self._indent()}{comp_name}() {{')
                self.indent_level += 1
                for line in comp_code.split('\n'):
                    if line.strip():
                        lines.append(f'{self._indent()}{line}')
                self.indent_level -= 1
                lines.append(f'{self._indent()}}},')
            self.indent_level -= 1
            lines.append(f'{self._indent()}}},')
            lines.append('')

        if getattr(component.script, "lifecycle", {}):
            for hook_name, hook_code in component.script.lifecycle.items():
                lines.append(f'{self._indent()}{hook_name}() {{')
                self.indent_level += 1
                for line in hook_code.split('\n'):
                    if line.strip():
                        lines.append(f'{self._indent()}{line}')
                self.indent_level -= 1
                lines.append(f'{self._indent()}}},')
            lines.append('')

        if getattr(component.script, "watch", {}):
            lines.append(f'{self._indent()}watch: {{')
            self.indent_level += 1
            for watch_name, watch_code in component.script.watch.items():
                lines.append(f'{self._indent()}{watch_name}(newValue, oldValue) {{')
                self.indent_level += 1
                for line in watch_code.split('\n'):
                    if line.strip():
                        lines.append(f'{self._indent()}{line}')
                self.indent_level -= 1
                lines.append(f'{self._indent()}}},')
            self.indent_level -= 1
            lines.append(f'{self._indent()}}},')
            lines.append('')
        
        # Template
        template_code = self._generate_template(nodes)
        # The generated component is intentionally runnable as a plain browser
        # ES module.  Keep the CSS/template contract together by embedding the
        # compiled stylesheet in the component runtime and installing it once
        # when the component mounts.  The standalone .css file is still emitted
        # by the build pipeline for deployments that prefer external CSS.
        style_code = self._generate_component_css(component)
        lines.append(f'{self._indent()}template: `{template_code}`,')
        
        self.indent_level -= 1
        lines.append('};')
        lines.append('')
        lines.extend(self._generate_runtime(component, template_code, style_code))
        lines.append('export default __component;')
        
        code = '\n'.join(lines)
        if self.minify:
            code = self._minify_generated_js(code)
        return code

    def _minify_generated_js(self, code: str) -> str:
        """Safely compact generated output without rewriting template strings."""
        lines = []
        for line in code.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith('// Generated by'):
                continue
            lines.append(stripped)
        return '\n'.join(lines)

    def _generate_component_css(self, component: Component) -> str:
        """Compile this component's CSS using the same scope identity as markup."""
        if not self.options.get("inline_css", True):
            return ""
        styles = getattr(component, "styles", None) or [component.style]
        if not any(style.css.strip() for style in styles):
            return ""
        from teloce.css.generator import CSSGenerator

        generated = []
        for style in styles:
            generated.append(CSSGenerator({
                **self.options,
                "scoped": style.scoped,
                "module": style.module,
            }).generate(style.css, component.name))
        return "\n".join(css for css in generated if css)

    def _generate_js_filters(self) -> str:
        """Serialize explicitly supplied browser filter implementations."""
        filters = self.options.get("filter_js", {}) or {}
        parts = []
        for name, source in filters.items():
            if isinstance(source, str):
                parts.append(f'{json.dumps(name)}: ({source})')
        return ", ".join(parts)

    def _generate_runtime(
        self,
        component: Component,
        template_code: str,
        style_code: str = "",
    ) -> List[str]:
        """Generate a dependency-free browser mount function.

        The compiler intentionally emits a small runtime per component for
        now. This keeps generated files usable without npm while the shared
        runtime API evolves.
        """
        template_literal = json.dumps(template_code, ensure_ascii=False)
        style_literal = json.dumps(style_code, ensure_ascii=False)
        style_classes_literal = json.dumps(self.module_mapping, ensure_ascii=False)
        data = component.script_data or "{}"
        imports = self._component_imports(component)
        component_map = ', '.join(f'{json.dumps(name)}: {name}' for name in imports)
        custom_filters = self._generate_js_filters()
        filter_suffix = f", {custom_filters}" if custom_filters else ""
        runtime = [
            SAFE_EXPRESSION_RUNTIME,
            f'const __components = {{{component_map}}};',
            'const __readProps = (element, parentState) => {',
            '  const slots = { default: "" }; for (const child of Array.from(element.childNodes)) { if (child.nodeType === 1 && child.hasAttribute("slot")) { const name = child.getAttribute("slot") || "default"; slots[name] = (slots[name] || "") + child.outerHTML; } else { slots.default += child.outerHTML ?? child.textContent ?? ""; } }',
            '  const props = { __slots: slots };',
            '  for (const attribute of Array.from(element.attributes)) {',
            '    if (attribute.name === "data-v-" || attribute.name.startsWith("data-v-") || attribute.name.startsWith("data-teloce-event-")) continue;',
            '    if (attribute.name === "data-teloce-is") { props.__dynamic = __evaluate(attribute.value, parentState); continue; }',
            '    if (attribute.name.startsWith(":")) props[attribute.name.slice(1)] = __evaluate(attribute.value, parentState);',
            '    else if (!attribute.name.startsWith("data-")) props[attribute.name] = attribute.value;',
            '  }',
            '  return props;',
            '};',
            f'const __template = {template_literal};',
            f'const __style = {style_literal};',
            f'const __styleClasses = {style_classes_literal};',
            'const __moduleUrl = typeof import.meta !== "undefined" ? import.meta.url.split("?")[0] : "";',
            'const __hmrRegistry = typeof globalThis !== "undefined" ? (globalThis.__teloce_hmr_instances ||= new Map()) : new Map();',
            'const __registerHmr = record => { if (!__moduleUrl) return; if (!__hmrRegistry.has(__moduleUrl)) __hmrRegistry.set(__moduleUrl, new Set()); __hmrRegistry.get(__moduleUrl).add(record); };',
            'const __unregisterHmr = record => { const records = __hmrRegistry.get(__moduleUrl); records?.delete(record); if (records?.size === 0) __hmrRegistry.delete(__moduleUrl); };',
            'if (typeof globalThis !== "undefined" && !globalThis.__teloce_hmr_reload) globalThis.__teloce_hmr_reload = async () => { const records = [...__hmrRegistry.values()].flatMap(set => [...set]); for (const record of records) await record.reload(); };',
            f'const __initialData = {data};',
            'const __normalizeProps = (input) => { const output = { ...input }; for (const [name, definition] of Object.entries(__component.props || {})) { if (output[name] === undefined && definition?.type === "Boolean") output[name] = false; if (output[name] === undefined && definition && definition.default !== null && definition.default !== undefined) { try { output[name] = Function(`return (${definition.default})`)(); } catch (_) {} } if (__dev && definition?.required && output[name] === undefined) console.warn(`Missing required prop: ${name}`); if (__dev && definition?.type && output[name] !== undefined) { const expected = String(definition.type).split("|"); const actual = output[name]?.constructor?.name; if (!expected.includes(actual)) console.warn(`Invalid prop type for ${name}: expected ${definition.type}, got ${actual}`); } if (definition?.validator && output[name] !== undefined) { try { const valid = Function(`return (${definition.validator})`)()(output[name]); if (__dev && !valid) console.warn(`Invalid prop value for ${name}`); } catch (error) { if (__dev) console.warn(`Prop validator failed for ${name}`, error); } } } return output; };',
            'const __installStyle = () => {',
            '  if (!__style || typeof document === "undefined") return;',
            f'  const styleId = "teloce-style-{HashGenerator().generate(component.name, length=9)}";',
            '  if (document.querySelector(`style[data-teloce-style="${styleId}"]`)) return;',
            '  const style = document.createElement("style");',
            '  style.dataset.teloceStyle = styleId;',
            '  style.setAttribute("data-teloce-style", styleId);',
            '  style.textContent = __style;',
            '  (document.head || document.documentElement).appendChild(style);',
            '};',
            f'const __filters = {{ uppercase: value => String(value ?? "").toUpperCase(), lowercase: value => String(value ?? "").toLowerCase(), trim: value => String(value ?? "").trim(), capitalize: value => {{ const text = String(value ?? ""); return text ? text[0].toUpperCase() + text.slice(1) : text; }}, slugify: value => String(value ?? "").trim().toLowerCase().replace(/[^\\w\\s-]/g, "").replace(/[\\s_-]+/g, "-").replace(/^-+|-+$/g, ""), truncate: (value, length = 30, suffix = "...") => {{ const text = String(value ?? ""); const size = Number(length); return text.length > size ? text.slice(0, Math.max(0, size - String(suffix).length)) + suffix : text; }}, currency: (value, currency = "USD") => new Intl.NumberFormat(undefined, {{ style: "currency", currency: String(currency).toUpperCase() }}).format(Number(value) || 0), percent: (value, digits = 0) => `${{(Number(value) * 100).toFixed(Number(digits))}}%`, number: (value, locale) => new Intl.NumberFormat(locale || undefined).format(Number(value) || 0), first: value => Array.isArray(value) ? value[0] : value, last: value => Array.isArray(value) ? value[value.length - 1] : value, pluck: (value, key) => Array.isArray(value) ? value.map(item => item == null ? undefined : item[key]) : value, orderBy: (value, key, direction = "asc") => Array.isArray(value) ? [...value].sort((a, b) => {{ const left = key == null ? a : a?.[key]; const right = key == null ? b : b?.[key]; const result = left < right ? -1 : left > right ? 1 : 0; return String(direction).toLowerCase() === "desc" ? -result : result; }}) : value, json: value => JSON.stringify(value), join: (value, separator = ", ") => Array.isArray(value) ? value.join(separator) : value{filter_suffix} }};',
            f'const __dev = {str(bool(self.dev)).lower()};',
            'const __legacyEvaluate = (expression, scope) => {',
            '  try { const parts = String(expression).split(/\\s+\\|\\s+/); let value = Function("scope", `with (scope) { return (${parts.shift()}) }`)(scope); for (const filter of parts) { const match = filter.match(/^([\\w$]+)(?:\\((.*)\\)|(?::(.*)))?$/); const argumentsSource = match?.[2] ?? match?.[3]; if (match && __filters[match[1]]) value = __filters[match[1]](value, ...(argumentsSource ? Function(`return [${argumentsSource.replace(/:/g, ",")}]`)() : [])); } return value; }',
            '  catch (error) { if (__dev) console.error("Teloce expression error:", expression, error); return ""; }',
            '};',
            'const __evaluate = (expression, scope) => { try { const parts = String(expression).split(/\\s+\\|\\s+/); let value = __safeEvaluate(parts.shift(), scope || {}); for (const filter of parts) { const match = filter.match(/^([\\w$]+)(?:\\((.*)\\)|(?::(.*)))?$/); const argumentsSource = match?.[2] ?? match?.[3]; if (match && __filters[match[1]]) value = __filters[match[1]](value, ...(argumentsSource ? argumentsSource.split(",").map(argument => __safeEvaluate(argument, scope || {})) : [])); } return value; } catch (error) { if (__dev) console.error("Teloce expression error:", expression, error); return ""; } };',
            "const __escapeHtml = (value) => String(value).replace(/[&<>\"']/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[character]));",
            'const __legacyAssign = (expression, value, scope) => { try { Function("scope", "value", `with (scope) { ${expression} = value }`)(scope, value); } catch (_) {} };',
            'const __assign = (expression, value, scope) => { try { const path = String(expression).trim().split(".").filter(Boolean); if (!path.length) return; if (path.length === 1) scope[path[0]] = value; else { let target = scope[path[0]]; for (const part of path.slice(1, -1)) target = target?.[part]; if (target != null) target[path[path.length - 1]] = value; } } catch (_) {} };',
            'const __mapClass = value => { const map = token => __styleClasses[token] || token; return Array.isArray(value) ? value.map(map).join(" ") : value && typeof value === "object" ? Object.keys(value).filter(key => value[key]).map(map).join(" ") : typeof value === "string" ? value.split(/\\s+/).filter(Boolean).map(map).join(" ") : value; };',
            'const __pluginDirectives = typeof globalThis !== "undefined" ? (globalThis.teloce?.directives || {}) : {};',
            'const __applyBinding = (element, name, value) => { if (name === "class") { element.className = __mapClass(value) ?? ""; } else if (name === "style" && value && typeof value === "object") { for (const [key, item] of Object.entries(value)) element.style[key] = item ?? ""; } else if (name === "show" || name === "hide") { element.hidden = name === "show" ? !Boolean(value) : Boolean(value); } else if (name === "html") { element.innerHTML = value == null ? "" : String(value); } else if (name === "text") { element.textContent = value == null ? "" : String(value); } else if (["disabled", "checked", "selected", "readonly", "required", "multiple"].includes(name)) { element.toggleAttribute(name, Boolean(value)); } else if (value === false || value == null) element.removeAttribute(name); else element.setAttribute(name, String(value)); };',
            'const __patch = (target, html) => {',
            '  const template = document.createElement("template"); template.innerHTML = html;',
            '  const disposeNode = node => { if (!node) return; if (node.__teloceInstance?.unmount) node.__teloceInstance.unmount(); if (node.__teloceHandlers) for (const record of node.__teloceHandlers.values()) node.removeEventListener(record.actualEvent, record.listener, record.options); for (const child of Array.from(node.childNodes || [])) disposeNode(child); };',
            '  const patchNode = (oldNode, newNode) => {',
            '    if (!oldNode || oldNode.nodeType !== newNode.nodeType || (oldNode.nodeType === 1 && oldNode.tagName !== newNode.tagName)) return newNode.cloneNode(true);',
            '    if (oldNode.nodeType === 3) { if (oldNode.nodeValue !== newNode.nodeValue) oldNode.nodeValue = newNode.nodeValue; return oldNode; }',
            '    const managedAttributes = oldNode.__teloceManagedAttributes || new Set(); for (const attr of Array.from(oldNode.attributes)) if (managedAttributes.has(attr.name) && !newNode.hasAttribute(attr.name)) oldNode.removeAttribute(attr.name);',
            '    for (const attr of Array.from(newNode.attributes)) if (oldNode.getAttribute(attr.name) !== attr.value) oldNode.setAttribute(attr.name, attr.value);',
            '    oldNode.__teloceManagedAttributes = new Set(Array.from(newNode.attributes).map(attribute => attribute.name));',
            '    patchChildren(oldNode, newNode); return oldNode;',
            '  };',
            '  const patchChildren = (parent, templateParent) => {',
            '    const old = Array.from(parent.childNodes); const next = Array.from(templateParent.childNodes); const keyed = new Map(old.filter(node => node.nodeType === 1 && node.dataset.teloceKey).map(node => [node.dataset.teloceKey, node])); const used = new Set();',
            '    next.forEach((newNode, index) => { const key = newNode.nodeType === 1 ? newNode.dataset.teloceKey : null; let oldNode = key && keyed.has(key) ? keyed.get(key) : old[index]; if (oldNode && used.has(oldNode)) oldNode = null; if (oldNode) used.add(oldNode); const result = oldNode ? patchNode(oldNode, newNode) : newNode.cloneNode(true); if (result !== oldNode) { if (oldNode && oldNode.parentNode === parent) { disposeNode(oldNode); parent.replaceChild(result, oldNode); } else parent.insertBefore(result, parent.childNodes[index] || null); } else if (result !== parent.childNodes[index]) parent.insertBefore(result, parent.childNodes[index] || null); });',
            '    for (const oldNode of old) if (!used.has(oldNode) && oldNode.parentNode === parent) { disposeNode(oldNode); parent.removeChild(oldNode); }',
            '  };',
            '  patchChildren(target, template.content);',
            '};',
            'const __renderTemplate = (source, state) => {',
            '  let output = source;',
            '  output = output.replace(/<if\\s+(?:condition|test)="([^"]*)">([\\s\\S]*?)(?:<else>([\\s\\S]*?))?<\\/if>/g, (_, test, yes, no) => __evaluate(test, state) ? yes : (no || ""));',
            '  output = output.replace(/<slot(?:\\s+name="([^"]*)")?\\s*><\\/slot>/g, (_, name) => (state.__slots || {})[name || "default"] || "");',
            '  const __renderLoops = (source, state) => {',
            '    let cursor = source.indexOf("<for ");',
            '    while (cursor >= 0) {',
            '      const openEnd = source.indexOf(">", cursor); if (openEnd < 0) break;',
            '      const opening = source.slice(cursor, openEnd + 1); const itemMatch = opening.match(/item="([^"]*)"/); const collectionMatch = opening.match(/(?:in|collection)="([^"]*)"/); if (!itemMatch || !collectionMatch) break;',
            '      let depth = 1; let scan = openEnd + 1; let closeStart = -1; while (depth && scan < source.length) { const nextOpen = source.indexOf("<for ", scan); const nextClose = source.indexOf("</for>", scan); if (nextClose < 0) break; if (nextOpen >= 0 && nextOpen < nextClose) { depth++; scan = nextOpen + 5; } else { depth--; closeStart = nextClose; scan = nextClose + 6; } } if (depth || closeStart < 0) break;',
            '      const body = source.slice(openEnd + 1, closeStart); const values = __evaluate(collectionMatch[1], state) || []; const rendered = Array.from(values).map((value, index) => { const loopScope = { ...state, [itemMatch[1]]: value, index }; const nested = __renderLoops(body, loopScope); return nested.replace(/data-teloce-bind-([\\w-]+)="([^"]*)"/g, (_, name, expression) => { const decoded = expression.replace(/&#x27;/g, "\\\'").replace(/&quot;/g, "\\\"").replace(/&amp;/g, "&"); const result = __evaluate(decoded, loopScope); const serialized = result && typeof result === "object" ? JSON.stringify(result) : String(result ?? ""); return `data-teloce-bind-${name}="${serialized.replace(/\\"/g, "&quot;")}"`; }).replace(/<if\\s+[^>]*?(?:condition|test)="([^"]*)"[^>]*>([\\s\\S]*?)(?:<else>([\\s\\S]*?))?<\\/if>/g, (_, test, yes, no) => __evaluate(test, loopScope) ? yes : (no || "")).replace(/{{\\s*([^{}]+?)\\s*}}/g, (_, expression) => { const result = __evaluate(expression, loopScope); return result == null ? "" : __escapeHtml(String(result)); }); }).join("");',
            '      source = source.slice(0, cursor) + rendered + source.slice(closeStart + 6); cursor = source.indexOf("<for ");',
            '    } return source;',
            '  };',
            '  output = __renderLoops(output, state);',
            '  output = output.replace(/{{\\s*([^{}]+?)\\s*}}/g, (_, expression) => { const value = __evaluate(expression, state); return value == null ? "" : __escapeHtml(String(value)); });',
            '  output = output.replace(/@([\\w.-]+)="([^"]*)"/g, "data-teloce-event-$1=\\"$2\\"");',
            '  output = output.replace(/:([\\w-]+)="([^"]*)"/g, (_, name, expression) => `${name}=\\"${String(__evaluate(expression, state) ?? "").replace(/\\\"/g, "&quot;")}\\"`);',
            '  return output;',
            '};',
            'export function mount(target, props = {}) {',
            '  if (typeof target === "string") target = document.querySelector(target);',
            '  if (!target) throw new Error("Teloce mount target was not found");',
            '  __installStyle();',
            '  let update = () => {}; let rendering = false; let updateQueued = false;',
            '  const requestUpdate = () => { if (rendering) { updateQueued = true; return; } rendering = true; try { update(); } finally { rendering = false; if (updateQueued) { updateQueued = false; queueMicrotask(requestUpdate); } } };',
            '  let mounted = false;',
            '  let previous = {};',
            '  const state = new Proxy(Object.assign({}, __initialData, __normalizeProps(props)), { set(object, key, value) { object[key] = value; requestUpdate(); return true; } });',
            '  state.$style = __styleClasses;',
            '  for (const [name, getter] of Object.entries(__component.computed || {})) Object.defineProperty(state, name, { enumerable: true, get: () => getter.call(state) });',
            '  const methods = __component.methods || {};',
            '  for (const [name, method] of Object.entries(methods)) state[name] = method.bind(state);',
            '  state.$emit = (name, detail) => target.dispatchEvent(new CustomEvent(`teloce:${name}`, { detail, bubbles: true }));',
            '  update = () => {',
            '    const wasMounted = mounted;',
            '    if (wasMounted && typeof __component.beforeUpdate === "function") __component.beforeUpdate.call(state);',
            '    if (!mounted && typeof __component.beforeMount === "function") __component.beforeMount.call(state);',
            '    __patch(target, __renderTemplate(__template, state));',
            '    const nativeEvents = new Set(["click", "input", "submit", "change", "keyup", "keydown", "focus", "blur", "mouseenter", "mouseleave"]);',
            '    target.querySelectorAll("*").forEach(element => {',
            '      for (const attribute of Array.from(element.attributes)) if (attribute.name.startsWith("data-teloce-event-")) {',
            '        const eventKey = attribute.name.slice("data-teloce-event-".length);',
            '        const [eventName, ...modifiers] = eventKey.split(".");',
            '        const handlerName = attribute.value;',
            '        const actualEvent = nativeEvents.has(eventName) ? eventName : `teloce:${eventName}`;',
            '        if (!element.__teloceHandlers) element.__teloceHandlers = new Map();',
            '        const previousHandler = element.__teloceHandlers.get(attribute.name); const signature = eventKey + "=" + handlerName;',
            '        if (!previousHandler || previousHandler.signature !== signature) { if (previousHandler) element.removeEventListener(previousHandler.actualEvent, previousHandler.listener, previousHandler.options); const listener = event => { if (modifiers.includes("self") && event.target !== element) return; if (modifiers.includes("enter") && event.key !== "Enter") return; if (modifiers.includes("esc") && event.key !== "Escape") return; if (modifiers.includes("ctrl") && !event.ctrlKey) return; if (modifiers.includes("shift") && !event.shiftKey) return; if (modifiers.includes("alt") && !event.altKey) return; if (modifiers.includes("meta") && !event.metaKey) return; if (modifiers.includes("right") && event.button !== 2) return; if (modifiers.includes("middle") && event.button !== 1) return; if (modifiers.includes("left") && event.button !== 0) return; if (modifiers.includes("prevent")) event.preventDefault(); if (modifiers.includes("stop")) event.stopPropagation(); const handler = state[handlerName]; if (typeof handler === "function") handler(event?.detail ?? event); else __evaluate(handlerName, { ...state, event, $event: event }); }; const options = { once: modifiers.includes("once"), capture: modifiers.includes("capture"), passive: modifiers.includes("passive") }; element.__teloceHandlers.set(attribute.name, { signature, actualEvent, listener, options }); element.addEventListener(actualEvent, listener, options); }',
            '      }',
            '      const model = element.getAttribute("data-teloce-model");',
            '      if (model) { const current = __evaluate(model, state); if (element.type === "checkbox") element.checked = Boolean(current); else if (element.value !== String(current ?? "")) element.value = current ?? ""; if (!element.__teloceModel) { element.__teloceModel = true; const eventName = element.type === "checkbox" || element.tagName === "SELECT" ? "change" : "input"; element.addEventListener(eventName, event => __assign(model, element.type === "checkbox" ? element.checked : element.value, state)); } }',
            '      for (const attribute of Array.from(element.attributes)) if (attribute.name.startsWith("data-teloce-bind-")) { const name = attribute.name.slice("data-teloce-bind-".length); __applyBinding(element, name, __evaluate(attribute.value, state)); }',
            '      for (const attribute of Array.from(element.attributes)) { const match = attribute.name.match(/^v-([\\w-]+)$/); const directive = match && __pluginDirectives[match[1]]; if (directive?.render) directive.render(element, { name: match[1], expression: attribute.value, value: __evaluate(attribute.value, state), state, modifiers: [] }); }',
            '    });',
            '    for (const [name, child] of Object.entries(__components)) {',
            '      target.querySelectorAll(name.toLowerCase()).forEach(element => {',
            '        if (!element.__teloceMounted && child && typeof child.mount === "function") {',
            '          element.__teloceMounted = true;',
            '          element.__teloceInstance = child.mount(element, __readProps(element, state));',
            '        } else if (element.__teloceInstance?.updateProps) { element.__teloceInstance.updateProps(__readProps(element, state)); }',
            '      });',
            '    }',
            '    target.querySelectorAll("teloce-dynamic").forEach(element => {',
            '      const name = __evaluate(element.getAttribute("data-teloce-is") || "", state);',
            '      const child = __components[name] || __components[String(name).replace(/^./, value => value.toUpperCase())];',
            '      if (!element.__teloceMounted && child && typeof child.mount === "function") { element.__teloceMounted = true; element.__teloceInstance = child.mount(element, __readProps(element, state)); } else if (element.__teloceInstance?.updateProps) { element.__teloceInstance.updateProps(__readProps(element, state)); }',
            '    });',
            '    if (!mounted && typeof __component.mounted === "function") __component.mounted.call(state);',
            '    mounted = true;',
            '    for (const [name, handler] of Object.entries(__component.watch || {})) { if (!Object.is(previous[name], state[name])) handler.call(state, state[name], previous[name]); previous[name] = state[name]; }',
            '    if (wasMounted && typeof __component.updated === "function") __component.updated.call(state);',
            '  };',
            '  update();',
            '  const updateProps = nextProps => { for (const [key, value] of Object.entries(__normalizeProps(nextProps))) state[key] = value; };',
            '  const __hmrRecord = { target, state, reload: async () => { const snapshot = {}; for (const key of Object.keys(state)) if (!key.startsWith("$") && typeof state[key] !== "function") snapshot[key] = state[key]; __unregisterHmr(__hmrRecord); const fresh = await import(`${__moduleUrl}?teloce_hmr=${Date.now()}`); return fresh.mount(target, snapshot); } }; __registerHmr(__hmrRecord);',
            '  const __instance = { state, update, updateProps, unmount: () => { if (typeof __component.beforeUnmount === "function") __component.beforeUnmount.call(state); __unregisterHmr(__hmrRecord); target.querySelectorAll("*").forEach(element => element.__teloceInstance?.unmount?.()); target.replaceChildren(); if (typeof __component.unmounted === "function") __component.unmounted.call(state); } }; __hmrRecord.instance = __instance; return __instance;',
            '}',
            'export const createApp = mount;',
            '__component.mount = mount;',
        ]
        return [line.replace("else __evaluate(handlerName", "else __runEventExpression(handlerName") for line in runtime]

    def _component_imports(self, component: Component) -> dict:
        """Return local component names and their generated import paths."""
        configured = self.options.get("component_imports", {})
        imports = {}
        pattern = r'import\s+([A-Za-z_$][\w$]*)(?:\s*,\s*\{[^}]*\})?\s+from\s+[\'\"]([^\'\"]+\.vel)[\'\"]'
        for match in re.finditer(pattern, component.script.raw):
            name, source = match.groups()
            imports[name] = configured.get(name, source[:-4] + ".js")
        named_pattern = r'import\s*\{([^}]+)\}\s*from\s+[\'\"]([^\'\"]+\.vel)[\'\"]'
        for match in re.finditer(named_pattern, component.script.raw):
            source = match.group(2)
            for item in match.group(1).split(','):
                parts = re.split(r'\s+as\s+', item.strip())
                name = parts[-1].strip()
                if name:
                    imports[name] = configured.get(name, source[:-4] + ".js")
        return imports

    def _generate_component_imports(self, component: Component) -> List[str]:
        """Emit browser imports for local `.vel` component dependencies."""
        configured = self.options.get("component_imports", {})
        lines = []
        emitted = set()
        for item in getattr(component.script, "imports", []):
            source = item.source
            if not source.endswith(".vel"):
                continue
            local = item.alias or (item.names[0] if item.names else "")
            path = configured.get(local, source[:-4] + ".js")
            if not local or (local, path, item.is_default, item.is_namespace) in emitted:
                continue
            emitted.add((local, path, item.is_default, item.is_namespace))
            if item.is_namespace:
                lines.append(f'import * as {local} from {json.dumps(path)};')
            elif item.is_default:
                lines.append(f'import {local} from {json.dumps(path)};')
            else:
                imported = item.names[0]
                binding = imported if imported == local else f'{imported} as {local}'
                lines.append(f'import {{ {binding} }} from {json.dumps(path)};')
        # Keep compatibility with manually constructed Component objects that
        # do not carry ScriptImport metadata.
        if not lines:
            lines.extend(
                f'import {name} from {json.dumps(path)};'
                for name, path in self._component_imports(component).items()
            )
        return lines
    
    def _generate_template(self, nodes: List[ASTNode]) -> str:
        """Generate template code from AST nodes."""
        result = []
        for node in nodes:
            result.append(self._generate_node(node))
        return ''.join(result)
    
    def _generate_node(self, node: ASTNode) -> str:
        """Generate code for a single node."""
        if isinstance(node, ElementNode):
            return self._generate_element(node)
        elif isinstance(node, TextNode):
            return self._generate_text(node)
        elif isinstance(node, InterpolationNode):
            return self._generate_interpolation(node)
        elif isinstance(node, ForNode):
            return self._generate_for(node)
        elif isinstance(node, IfNode):
            return self._generate_if(node)
        else:
            return ''
    
    def _generate_element(self, node: ElementNode) -> str:
        """Generate code for an element."""
        tag = node.tag
        attrs = []

        dynamic_expression = None
        if tag.lower() == "component":
            for binding in node.bindings:
                if binding.name == "is":
                    dynamic_expression = binding.value
                    break
            tag = "teloce-dynamic"
            if dynamic_expression:
                attrs.append(f'data-teloce-is="{html.escape(dynamic_expression, quote=True)}"')

        if self.scope_id and not any(name.startswith('data-v-') for name in node.attributes):
            attrs.append(f'{self.scope_id}=""')
        
        # Regular attributes
        for name, value in node.attributes.items():
            if name == "class" and self.module_mapping:
                value = " ".join(self.module_mapping.get(token, token) for token in str(value).split())
            attrs.append(f'{name}="{html.escape(str(value), quote=True)}"')
        
        # Bindings
        for binding in node.bindings:
            if dynamic_expression is not None and binding.name == "is":
                continue
            if binding.name == 'model':
                attrs.append(f'data-teloce-model="{html.escape(binding.value, quote=True)}"')
            elif binding.name == 'class':
                attrs.append(f'data-teloce-bind-class="{html.escape(binding.value, quote=True)}"')
            elif binding.name == 'style':
                attrs.append(f'data-teloce-bind-style="{html.escape(binding.value, quote=True)}"')
            elif binding.name == 'show':
                attrs.append(f'data-teloce-bind-show="{html.escape(binding.value, quote=True)}"')
            elif binding.name == 'hide':
                attrs.append(f'data-teloce-bind-hide="{html.escape(binding.value, quote=True)}"')
            else:
                attrs.append(f'data-teloce-bind-{binding.name}="{html.escape(binding.value, quote=True)}"')
        
        # Events
        for event in node.events:
            attrs.append(f'@{event.name}="{event.handler}"')
        
        # Build opening tag
        attrs_str = ' ' + ' '.join(attrs) if attrs else ''
        opening = f'<{tag}{attrs_str}>'
        
        # Children
        children_html = self._generate_template(node.children)
        
        # Closing tag
        closing = '' if ElementFactory.is_void(tag) else f'</{tag}>'
        
        return f'{opening}{children_html}{closing}'
    
    def _generate_text(self, node: TextNode) -> str:
        """Generate code for text."""
        return node.value
    
    def _generate_interpolation(self, node: InterpolationNode) -> str:
        """Generate code for interpolation."""
        return f'{{{{ {node.expression} }}}}'
    
    def _generate_for(self, node: ForNode) -> str:
        """Generate code for for loop."""
        item = node.item or 'item'
        collection = node.collection or 'items'
        key = node.key or 'index'
        
        children = self._generate_template(node.children)
        if node.key and node.key != "index":
            # Give the DOM reconciler a stable identity for each repeated row.
            key_expression = node.key if "." in node.key or node.key == item else f"{item}.{node.key}"
            children = re.sub(
                r"<([A-Za-z][\w:-]*)",
                rf'<\1 data-teloce-key="{{{{ {key_expression} }}}}"',
                children,
                count=1,
            )
        return f'<for key="{key}" item="{item}" in="{collection}">{children}</for>'
    
    def _generate_if(self, node: IfNode) -> str:
        """Generate code for if statement."""
        condition = node.condition or 'condition'
        
        children = self._generate_template(node.children)
        
        if node.else_children:
            else_children = self._generate_template(node.else_children)
            return f'<if condition="{condition}">{children}<else>{else_children}</if>'
        
        return f'<if condition="{condition}">{children}</if>'
    
    def _indent(self) -> str:
        """Get the current indentation."""
        return '  ' * self.indent_level
