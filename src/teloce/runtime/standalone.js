/* Teloce standalone runtime for Jinja/static HTML and CDN-style usage. */
(function (root) {
  "use strict";
  const filters = {
    uppercase: value => String(value ?? "").toUpperCase(),
    lowercase: value => String(value ?? "").toLowerCase(),
    trim: value => String(value ?? "").trim(),
    capitalize: value => { const text = String(value ?? ""); return text ? text[0].toUpperCase() + text.slice(1) : text; },
    slugify: value => String(value ?? "").trim().toLowerCase().replace(/[^\w\s-]/g, "").replace(/[\s_-]+/g, "-").replace(/^-+|-+$/g, ""),
    truncate: (value, length = 30, suffix = "...") => { const text = String(value ?? ""); const size = Number(length); return text.length > size ? text.slice(0, Math.max(0, size - String(suffix).length)) + suffix : text; },
    currency: (value, currency = "USD") => new Intl.NumberFormat(undefined, { style: "currency", currency: String(currency).toUpperCase() }).format(Number(value) || 0),
    percent: (value, digits = 0) => `${(Number(value) * 100).toFixed(Number(digits))}%`,
    number: (value, locale) => new Intl.NumberFormat(locale || undefined).format(Number(value) || 0),
    first: value => Array.isArray(value) ? value[0] : value,
    last: value => Array.isArray(value) ? value[value.length - 1] : value,
    pluck: (value, key) => Array.isArray(value) ? value.map(item => item == null ? undefined : item[key]) : value,
    orderBy: (value, key, direction = "asc") => Array.isArray(value) ? [...value].sort((a, b) => { const left = key == null ? a : a?.[key]; const right = key == null ? b : b?.[key]; const result = left < right ? -1 : left > right ? 1 : 0; return String(direction).toLowerCase() === "desc" ? -result : result; }) : value,
    json: value => JSON.stringify(value),
    join: (value, separator = ", ") => Array.isArray(value) ? value.join(separator) : value,
  };
  const plugins = [];
  const directives = Object.create(null);
  const components = Object.create(null);
  const helpers = Object.create(null);
  const escapeHtml = value => String(value ?? "").replace(/[&<>\"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
  const evaluate = (expression, scope) => {
    try {
      const parts = String(expression).split(/\s+\|\s+/);
      let value = Function("scope", "helpers", `with (helpers) { with (scope) { return (${parts.shift()}) } }`)(scope, helpers);
      for (const part of parts) {
        const match = part.match(/^([\w$]+)(?:\((.*)\)|(?::(.*)))?$/);
        const argumentsSource = match?.[2] ?? match?.[3];
        if (match && filters[match[1]]) value = filters[match[1]](value, ...(argumentsSource ? Function(`return [${argumentsSource.replace(/:/g, ",")}]`)() : []));
      }
      return value;
    } catch (_) { return ""; }
  };
  const assign = (expression, value, scope) => {
    try { Function("scope", "value", `with (scope) { ${expression} = value }`)(scope, value); } catch (_) {}
  };
  const runEventExpression = (expression, state, event) => {
    const source = String(expression).trim();
    const method = source.match(/^([\w$]+)\s*$/);
    if (method && typeof state[method[1]] === "function") return state[method[1]].call(state, event);
    const call = source.match(/^([\w$]+)\s*\(\s*\)$/);
    if (call && typeof state[call[1]] === "function") return state[call[1]].call(state, event);
    return evaluate(expression, state);
  };
  const registerPluginDirectives = plugin => {
    if (Array.isArray(plugin?.directives)) {
      for (const directive of plugin.directives) if (directive?.name) directives[directive.name] = directive;
    } else if (plugin?.directives && typeof plugin.directives === "object") {
      Object.assign(directives, plugin.directives);
    }
  };
  const registerComponent = (name, component) => {
    if (name && typeof name === "object") {
      component = name.component || name;
      name = name.name;
    }
    if (name && component) components[String(name).toLowerCase()] = component;
  };
  const registerHelper = (name, helper) => {
    if (name && helper !== undefined) helpers[name] = helper;
  };
  const registerPluginComponents = plugin => {
    if (Array.isArray(plugin?.components)) {
      for (const entry of plugin.components) registerComponent(entry?.name, entry?.component || entry);
    } else if (plugin?.components && typeof plugin.components === "object") {
      for (const [name, component] of Object.entries(plugin.components)) registerComponent(name, component?.component || component);
    }
  };
  const renderLoops = (source, scope) => source.replace(/<for\s+[^>]*item="([^"]*)"[^>]*in="([^"]*)"[^>]*>([\s\S]*?)<\/for>/g, (_, item, collection, body) => {
    const values = evaluate(collection, scope) || [];
    return Array.from(values).map((value, index) => render(body, { ...scope, [item]: value, index })).join("");
  });
  const renderLongFormLoops = (source, scope) => source.replace(/<([A-Za-z][\w:-]*)([^>]*?)v-for="([^"]+)"([^>]*)>([\s\S]*?)<\/\1>/g, (_, tag, before, expression, after, body) => {
    const match = expression.match(/^\s*(?:\(([^)]+)\)|([^\s]+))\s+(?:in|of)\s+(.+?)\s*$/);
    if (!match) return _;
    const variables = (match[1] || match[2]).split(",").map(value => value.trim());
    const values = evaluate(match[3], scope) || [];
    return Array.from(values).map((value, index) => render(body, { ...scope, [variables[0]]: value, [variables[1] || "index"]: index, index })).map((content, index) => `<${tag}${before.replace(/:key="[^"]*"|v-bind:key="[^"]*"/g, "")}${after}>${content}</${tag}>`).join("");
  });
  const renderLongFormConditionals = (source, scope) => {
    const stripBranch = attributes => attributes.replace(/\s+v-(?:if|else-if|else)(?:="[^"]*")?/g, "");
    let output = source;
    const branchPattern = /<([A-Za-z][\w:-]*)([^>]*?)v-if="([^"]+)"([^>]*)>([\s\S]*?)<\/\1>\s*<\1([^>]*?)v-(else-if|else)(?:="([^"]*)")?([^>]*)>([\s\S]*?)<\/\1>/g;
    let previous;
    do {
      previous = output;
      output = output.replace(branchPattern, (_, tag, firstBefore, condition, firstAfter, yes, secondBefore, branch, branchCondition, secondAfter, no) => {
        const firstAttributes = stripBranch(`${firstBefore}${firstAfter}`);
        if (evaluate(condition, scope)) return `<${tag}${firstAttributes}>${yes}</${tag}>`;
        if (branch === "else") return `<${tag}${stripBranch(`${secondBefore}${secondAfter}`)}>${no}</${tag}>`;
        const nextAttributes = stripBranch(`${secondBefore}${secondAfter}`);
        return `<${tag}${nextAttributes} v-if="${String(branchCondition || "").replace(/"/g, "&quot;")}">${no}</${tag}>`;
      });
    } while (output !== previous && /v-(?:if|else-if|else)=?/.test(output));
    return output;
  };
  const renderLongFormIfs = (source, scope) => source.replace(/<([A-Za-z][\w:-]*)([^>]*?)v-if="([^"]+)"([^>]*)>([\s\S]*?)<\/\1>/g, (_, tag, before, condition, after, body) => evaluate(condition, scope) ? `<${tag}${before}${after}>${body}</${tag}>` : "");
  const render = (source, scope) => {
    let output = renderLongFormLoops(source, scope);
    output = renderLongFormConditionals(output, scope);
    output = renderLongFormIfs(output, scope);
    output = renderLoops(output, scope);
    output = output.replace(/<if\s+(?:condition|test)="([^"]*)">([\s\S]*?)(?:<else>([\s\S]*?))?<\/if>/g, (_, test, yes, no) => evaluate(test, scope) ? yes : (no || ""));
    output = output.replace(/{{\s*([^{}]+?)\s*}}/g, (_, expression) => escapeHtml(evaluate(expression, scope)));
    output = output.replace(/@([\w.-]+)="([^"]*)"/g, 'data-teloce-event-$1="$2"');
    output = output.replace(/v-on:([\w.-]+)="([^"]*)"/g, 'data-teloce-event-$1="$2"');
    output = output.replace(/v-model="([^"]*)"/g, 'data-teloce-model="$1"');
    output = output.replace(/:([\w-]+)="([^"]*)"/g, (_, name, expression) => name === "model" ? `data-teloce-model="${expression}"` : `${name}="${String(evaluate(expression, scope) ?? "").replace(/\"/g, "&quot;")}"`);
    output = output.replace(/v-bind:([\w-]+)="([^"]*)"/g, (_, name, expression) => `data-teloce-bind-${name}="${String(evaluate(expression, scope) ?? "").replace(/\"/g, "&quot;")}"`);
    output = output.replace(/v-show="([^"]*)"/g, (_, expression) => `data-teloce-bind-show="${String(evaluate(expression, scope) ?? "").replace(/\"/g, "&quot;")}"`);
    output = output.replace(/v-text="([^"]*)"/g, (_, expression) => `data-teloce-bind-text="${String(evaluate(expression, scope) ?? "").replace(/\"/g, "&quot;")}"`);
    output = output.replace(/v-html="([^"]*)"/g, (_, expression) => `data-teloce-bind-html="${String(evaluate(expression, scope) ?? "").replace(/\"/g, "&quot;")}"`);
    return output;
  };
  const componentProps = (element, state) => {
    const props = {};
    for (const attribute of Array.from(element.attributes)) {
      if (attribute.name.startsWith("data-teloce-") || attribute.name.startsWith("v-") || attribute.name.startsWith("@")) continue;
      props[attribute.name] = attribute.value;
    }
    return props;
  };
  const renderPluginComponents = (target, state) => {
    for (const element of Array.from(target.querySelectorAll("*"))) {
      const component = components[element.tagName.toLowerCase()];
      if (!component || element.__teloceComponentRendered) continue;
      const props = componentProps(element, state);
      const renderComponent = typeof component === "function" ? component : component.render;
      if (typeof renderComponent !== "function") continue;
      const result = renderComponent(element, props, { state, target });
      if (result instanceof Node) element.replaceChildren(result);
      else if (typeof result === "string") element.innerHTML = result;
      element.__teloceComponentRendered = true;
      component.mounted?.(element, props, { state, target });
    }
  };
  function createApp(target, initial = {}) {
    if (typeof target === "string") target = document.querySelector(target);
    if (!target) throw new Error("Teloce mount target was not found");
    const source = target.innerHTML;
    let update = () => {};
    const proxyCache = new WeakMap();
    const makeReactive = value => {
      if (!value || typeof value !== "object") return value;
      if (proxyCache.has(value)) return proxyCache.get(value);
      const proxy = new Proxy(value, {
        get(object, key) { return makeReactive(Reflect.get(object, key)); },
        set(object, key, next) { const changed = object[key] !== next; const result = Reflect.set(object, key, next); if (changed) update(); return result; },
        deleteProperty(object, key) { const existed = Object.prototype.hasOwnProperty.call(object, key); const result = Reflect.deleteProperty(object, key); if (existed) update(); return result; },
      });
      proxyCache.set(value, proxy);
      return proxy;
    };
    const state = makeReactive({ ...initial });
    const instance = { target, state, mount: () => { update(); return instance; }, unmount: () => target.replaceChildren() };
    update = () => {
      for (const plugin of plugins) plugin.hooks?.beforeRender?.(state, { target });
      target.innerHTML = render(source, state);
      renderPluginComponents(target, state);
      target.querySelectorAll("*").forEach(element => {
        for (const attribute of Array.from(element.attributes)) {
          if (attribute.name.startsWith("data-teloce-event-")) {
            const eventKey = attribute.name.slice("data-teloce-event-".length); const [eventName, ...modifiers] = eventKey.split(".");
            const options = { once: modifiers.includes("once"), capture: modifiers.includes("capture"), passive: modifiers.includes("passive") };
            element.addEventListener(eventName, event => { if (modifiers.includes("self") && event.target !== element) return; if (modifiers.includes("enter") && event.key !== "Enter") return; if (modifiers.includes("esc") && event.key !== "Escape") return; if (modifiers.includes("ctrl") && !event.ctrlKey) return; if (modifiers.includes("shift") && !event.shiftKey) return; if (modifiers.includes("alt") && !event.altKey) return; if (modifiers.includes("meta") && !event.metaKey) return; if (modifiers.includes("right") && event.button !== 2) return; if (modifiers.includes("middle") && event.button !== 1) return; if (modifiers.includes("left") && event.button !== 0) return; if (modifiers.includes("prevent")) event.preventDefault(); if (modifiers.includes("stop")) event.stopPropagation(); state.event = event; state.$event = event; runEventExpression(attribute.value, state, event); }, options);
          }
          if (attribute.name === "data-teloce-model") {
            const expression = attribute.value; const eventName = element.type === "checkbox" || element.tagName === "SELECT" ? "change" : "input";
            element.addEventListener(eventName, () => assign(expression, element.type === "checkbox" ? element.checked : element.value, state));
          }
          if (attribute.name.startsWith("data-teloce-bind-")) {
            const name = attribute.name.slice("data-teloce-bind-".length);
            const value = attribute.value;
            if (name === "show") element.hidden = !Boolean(value && value !== "false");
            else if (name === "text") element.textContent = value;
            else if (name === "html") element.innerHTML = value;
            else if (value === "false" || value === "null" || value === "undefined") element.removeAttribute(name);
            else element.setAttribute(name, value);
          }
          const directiveMatch = attribute.name.match(/^v-([\w-]+)$/);
          const directive = directiveMatch && directives[directiveMatch[1]];
          if (directive?.render) {
            const expression = attribute.value;
            directive.render(element, {
              name: directiveMatch[1],
              expression,
              value: evaluate(expression, state),
              state,
              modifiers: [],
            });
          }
        }
      });
      for (const plugin of plugins) {
        plugin.updated?.(target, state);
        plugin.hooks?.afterRender?.(target, { state });
      }
    };
    update();
    for (const plugin of plugins) plugin.mounted?.(target, state);
    return instance;
  }
  const api = { createApp, create: createApp, mount: createApp, directives, components, helpers, registerComponent, registerHelper, use(plugin) {
    plugins.push(plugin);
    registerPluginDirectives(plugin);
    registerPluginComponents(plugin);
    if (plugin?.helpers && typeof plugin.helpers === "object") Object.assign(helpers, plugin.helpers);
    if (Array.isArray(plugin?.filters)) for (const filter of plugin.filters) if (filter?.name && filter.transform) filters[filter.name] = filter.transform;
    if (plugin?.filters && !Array.isArray(plugin.filters) && typeof plugin.filters === "object") Object.assign(filters, plugin.filters);
    plugin?.install?.(api);
    plugin?.hooks?.init?.(api);
    return api;
  }, filters, version: "0.1.0" };
  root.teloce = root.teloce || api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof globalThis !== "undefined") globalThis.teloce = root.teloce;
})(typeof globalThis !== "undefined" ? globalThis : window);
