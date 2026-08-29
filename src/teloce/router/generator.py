"""
Router generator - generates JavaScript router code.

Generates client-side router JavaScript from router configuration.
"""

from typing import List, Dict, Any, Optional
import json
from teloce.router.compiler import RouterConfig, Route


class RouterGenerator:
    """
    Generates JavaScript router code.
    """
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}
        self.minify = self.options.get('minify', False)
        self.indent_level = 0
    
    def generate(self, config: RouterConfig) -> str:
        """
        Generate JavaScript router code.
        
        Args:
            config: The router configuration
            
        Returns:
            Generated JavaScript code.
        """
        self.indent_level = 0
        lines = []
        
        lines.append('// Generated router by Teloce-Py')
        lines.append('')
        
        # Keep generated routers dependency-free so Python projects do not
        # need npm.  Applications can still replace this with @teloce/router
        # through a custom bundling step.
        lines.extend([
            'const createRouter = (routes, options = {}) => {',
            '  const state = { path: "", params: {}, query: {}, route: null, fullPath: "" };',
            '  const makeSignal = initial => { let value = initial; const subscribers = new Set(); const signal = () => value; signal.get = signal; signal.set = next => { value = next; subscribers.forEach(listener => listener(value)); }; signal.subscribe = listener => { subscribers.add(listener); return () => subscribers.delete(listener); }; return signal; };',
            '  const pathSignal = makeSignal(""); const paramsSignal = makeSignal({}); const querySignal = makeSignal({}); const routeSignal = makeSignal(null);',
            '  const listeners = new Set();',
            '  const guards = [];',
            '  const afterHooks = new Set(); let destroyed = false;',
            '  const normalize = path => (path || "/").replace(/\\/+$/, "") || "/";',
            '  const patternFor = routePath => { const names = []; let source = "^"; for (const segment of normalize(routePath).split("/").filter(Boolean)) { if (segment.startsWith(":") && segment.endsWith("?")) { names.push(segment.slice(1, -1)); source += "(?:/([^/]+))?"; } else if (segment.startsWith(":")) { names.push(segment.slice(1)); source += "/([^/]+)"; } else if (segment.startsWith("*")) { names.push(segment.slice(1) || "pathMatch"); source += "/(.*)"; } else source += "/" + segment.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&"); } return { pattern: new RegExp(source + "/?$"), names }; };',
            '  const match = (path, definitions, parent = "") => {',
            '    for (const route of definitions) {',
            '      const full = normalize(route.path.startsWith("/") ? route.path : `${parent}/${route.path}`);',
            '      const compiled = patternFor(full);',
            '      const found = normalize(path).match(compiled.pattern);',
            '      if (found) return { route, params: Object.fromEntries(compiled.names.map((name, index) => [name, found[index + 1] == null ? undefined : decodeURIComponent(found[index + 1])])) };',
            '      if (route.children) { const child = match(path, route.children, full); if (child) return child; }',
            '    }',
            '    return null;',
            '  };',
            '  const notify = () => listeners.forEach(listener => listener(state));',
            '  const parseQuery = query => { const result = {}; for (const [key, value] of new URLSearchParams(query || "")) result[key] = result[key] === undefined ? value : Array.isArray(result[key]) ? [...result[key], value] : [result[key], value]; return result; };',
            '  const queryString = query => { const params = new URLSearchParams(); for (const [key, value] of Object.entries(query || {})) for (const item of Array.isArray(value) ? value : [value]) params.append(key, item); const result = params.toString(); return result ? `?${result}` : ""; };',
            '  const navigate = async target => { if (destroyed) return false;',
            '    const descriptor = typeof target === "string" ? { path: target } : (target || {}); const raw = String(descriptor.path || "/"); const [rawPath, rawQuery = ""] = raw.split("?"); const next = normalize(rawPath); const encodedQuery = descriptor.query ? queryString(descriptor.query).slice(1) : rawQuery; const resolved = match(next, routes);',
            '    if (!resolved) return false;',
            '    if (resolved?.route.redirect) return navigate(resolved.route.redirect);',
            '    for (const guard of guards) { const decision = await guard({ path: next, params: resolved.params, query: parseQuery(encodedQuery), route: resolved.route }, { path: state.path, params: state.params, query: state.query, route: state.route }); if (decision === false) return false; if (typeof decision === "string") return navigate(decision); }',
            '    if (destroyed) return false; const previous = { path: state.path, params: state.params, query: state.query, route: state.route, fullPath: state.fullPath }; state.path = next; state.params = resolved.params || {}; state.query = parseQuery(encodedQuery); state.route = resolved.route || null; state.fullPath = next + (encodedQuery ? `?${encodedQuery}` : ""); pathSignal.set(state.path); paramsSignal.set(state.params); querySignal.set(state.query); routeSignal.set(state.route); notify(); afterHooks.forEach(hook => hook({ ...state }, previous)); return true;',
            '  };',
            '  const read = () => { const raw = options.mode === "history" ? `${location.pathname}${location.search}` : (location.hash.slice(1) || "/"); const base = normalize(options.base || "/"); return base !== "/" && raw.startsWith(base) ? raw.slice(base.length) || "/" : raw; };',
            '  const onLocation = () => navigate(read());',
            '  if (typeof window !== "undefined") window.addEventListener(options.mode === "history" ? "popstate" : "hashchange", onLocation);',
            '  const changeUrl = (target, replace) => { const descriptor = typeof target === "string" ? { path: target } : (target || {}); const path = String(descriptor.path || "/"); const urlPath = normalize(options.base || "/") === "/" ? path : `${normalize(options.base || "/")}${path.replace(/^\\//, "")}`; const url = urlPath + (descriptor.query ? queryString(descriptor.query) : (path.includes("?") ? "" : "")); if (options.mode === "history") (replace ? history.replaceState : history.pushState).call(history, {}, "", url); else location.hash = urlPath + (descriptor.query ? queryString(descriptor.query) : ""); };',
            '  const router = { state, options, path: pathSignal, params: paramsSignal, query: querySignal, currentRoute: routeSignal, navigate: async target => { const accepted = await navigate(target); if (accepted) changeUrl(target, false); return accepted; }, push: async target => { const accepted = await navigate(target); if (accepted) changeUrl(target, false); return accepted; }, replace: async target => { const accepted = await navigate(target); if (accepted) changeUrl(target, true); return accepted; }, back: () => history.back(), forward: () => history.forward(), go: delta => history.go(delta), beforeEach: guard => { guards.push(guard); return () => { const index = guards.indexOf(guard); if (index >= 0) guards.splice(index, 1); }; }, afterEach: hook => { if (typeof hook !== "function") return () => {}; afterHooks.add(hook); return () => afterHooks.delete(hook); }, subscribe: listener => { listeners.add(listener); return () => listeners.delete(listener); }, resolve: path => { const [pathname, query = ""] = String(path).split("?"); const resolved = match(normalize(pathname), routes); return resolved && { ...resolved, query: parseQuery(query), fullPath: normalize(pathname) + (query ? `?${query}` : "") }; }, mount: (container, context = {}) => { const view = createRouterView(router, container, (component, routeState, target) => { if (component?.mount) return component.mount(target, { ...context, ...routeState.params, ...routeState.query }); if (component?.template) { component.template(target, { ...routeState, ...context }); return component; } return null; }); return () => view.unmount(); }, destroy: () => { if (destroyed) return; destroyed = true; if (typeof window !== "undefined") window.removeEventListener(options.mode === "history" ? "popstate" : "hashchange", onLocation); guards.length = 0; listeners.clear(); afterHooks.clear(); } };',
            '  if (typeof window !== "undefined") navigate(read());',
            '  return router;',
            '};',
            'const createRoute = definition => definition;',
            'const createRouterView = (router, container, render) => { let active = null; const update = () => { if (!container) return; active?.unmount?.(); active = null; container.replaceChildren(); const component = router.state.route?.component; if (typeof render === "function") active = render(component, router.state, container) || null; else if (component?.mount) active = component.mount(container, router.state); }; const stop = router.subscribe(update); update(); return { update, unmount: () => { stop(); active?.unmount?.(); router.destroy?.(); container?.replaceChildren(); } }; };',
            'const createRouterLink = (router, to, label, options = {}) => { const link = document.createElement("a"); link.href = options.mode === "history" ? to : `#${to}`; link.textContent = label ?? to; link.addEventListener("click", event => { event.preventDefault(); router.push(to); }); const refresh = () => { const current = router.state.path; const exact = current === to; link.classList.toggle(options.linkExactActiveClass || router.options?.linkExactActiveClass || "exact-active", exact); link.classList.toggle(options.linkActiveClass || router.options?.linkActiveClass || "active", exact || current.startsWith(`${to}/`)); }; const stop = router.subscribe(refresh); refresh(); link.destroy = () => { stop(); link.remove(); }; return link; };',
            '',
        ])
        
        # Generate routes
        routes_code = self._generate_routes(config.routes)
        lines.append(f"const routes = {routes_code};")
        lines.append('')
        
        # Create router
        mode = config.mode
        base = config.base
        active_class = config.link_active_class
        exact_active_class = config.link_exact_active_class
        
        lines.append(f"const router = createRouter(routes, {{")
        self.indent_level += 1
        lines.append(f"{self._indent()}mode: {json.dumps(mode)},")
        lines.append(f"{self._indent()}base: {json.dumps(base)},")
        lines.append(f"{self._indent()}linkActiveClass: {json.dumps(active_class)},")
        lines.append(f"{self._indent()}linkExactActiveClass: {json.dumps(exact_active_class)},")
        self.indent_level -= 1
        lines.append("});")
        lines.append('')
        
        # Export router
        lines.append("export default router;")
        
        return '\n'.join(lines)
    
    def _generate_routes(self, routes: List[Route]) -> str:
        """Generate routes code."""
        route_strings = []
        
        for route in routes:
            route_strings.append(self._generate_route(route))
        
        return f"[{', '.join(route_strings)}]"
    
    def _generate_route(self, route: Route) -> str:
        """Generate a single route code."""
        parts = []
        
        # Path
        parts.append(f"path: {json.dumps(route.path)}")
        
        # Component (if not redirect)
        if route.component:
            parts.append(f"component: {route.component}")
        
        # Redirect
        if route.redirect:
            parts.append(f"redirect: {json.dumps(route.redirect)}")
        
        # Name
        if route.name:
            parts.append(f"name: {json.dumps(route.name)}")
        
        # Props
        if route.props:
            parts.append("props: true")
        
        # Children
        if route.children:
            children = self._generate_routes(route.children)
            parts.append(f"children: {children}")
        
        # Meta
        if route.meta:
            meta_str = self._generate_meta(route.meta)
            parts.append(f"meta: {meta_str}")
        
        return f"{{{', '.join(parts)}}}"
    
    def _generate_meta(self, meta: Dict[str, Any]) -> str:
        """Generate meta data code."""
        parts = []
        for key, value in meta.items():
            if isinstance(value, str):
                parts.append(f"{json.dumps(str(key))}: {json.dumps(value)}")
            else:
                parts.append(f"{key}: {value}")
        return f"{{{', '.join(parts)}}}"
    
    def _indent(self) -> str:
        """Get the current indentation."""
        return '  ' * self.indent_level
