"""
Helper functions for JavaScript generation.
"""

from typing import List, Optional, Dict, Any
import re


class HelperGenerator:
    """
    Generates JavaScript helper functions.
    """
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}
        self.minify = self.options.get('minify', False)
    
    def generate_signal_helpers(self) -> str:
        """Generate helper functions for signals."""
        return """
// Signal helpers
function createSignal(initial) {
    let value = initial;
    const subscribers = new Set();
    function signal(...args) {
        if (args.length) {
            const next = args[0];
            if (Object.is(value, next)) return value;
            value = next;
            [...subscribers].forEach(effect => effect.run());
        } else if (currentEffect) {
            subscribers.add(currentEffect);
            currentEffect.dependencies.add(subscribers);
        }
        return value;
    }
    signal.get = () => signal();
    signal.set = value => signal(value);
    signal.update = updater => signal(updater(signal()));
    signal.peek = () => value;
    signal.subscribe = listener => { const effect = listener.run ? listener : { run: listener }; subscribers.add(effect); return () => subscribers.delete(effect); };
    signal.__teloce_signal = true;
    return signal;
}

function createEffect(fn) {
    const effect = {
        dependencies: new Set(),
        stopped: false,
        run() {
            if (this.stopped) return;
            this.dependencies.forEach(dependency => dependency.delete(this));
            this.dependencies.clear();
            const prev = currentEffect;
            currentEffect = this;
            try { return fn(); } finally { currentEffect = prev; }
        },
        stop() { this.stopped = true; this.dependencies.forEach(dependency => dependency.delete(this)); this.dependencies.clear(); }
    };
    effect.run();
    return effect;
}

function createComputed(fn) {
    const result = createSignal();
    result.__teloce_computed = true;
    result.effect = createEffect(() => result(fn()));
    return result;
}
"""
    
    def generate_component_helpers(self) -> str:
        """Generate helper functions for components."""
        return """
// Component helpers
function createComponent(options) {
    return options;
}

function mount(component, target) {
    const ctx = component.data ? component.data() : {};
    
    // Add methods
    if (component.methods) {
        Object.keys(component.methods).forEach(key => {
            ctx[key] = component.methods[key].bind(ctx);
        });
    }
    
    // Add computed
    if (component.computed) {
        Object.keys(component.computed).forEach(key => {
            Object.defineProperty(ctx, key, {
                get: component.computed[key].bind(ctx)
            });
        });
    }
    
    // Mount lifecycle
    if (component.beforeMount) component.beforeMount.call(ctx);
    
    const el = component.render(ctx);
    target.appendChild(el);
    
    if (component.mounted) component.mounted.call(ctx);
    
    return ctx;
}

function unmount(component, target) {
    if (component.beforeUnmount) component.beforeUnmount();
    target.innerHTML = '';
    if (component.unmounted) component.unmounted();
}
"""
    
    def generate_reactive_helpers(self) -> str:
        """Generate reactive helpers."""
        return """
// Reactive helpers
let currentEffect = null;

function batch(fn) {
    const prev = currentEffect;
    currentEffect = null;
    fn();
    currentEffect = prev;
}

function untracked(fn) {
    const prev = currentEffect;
    currentEffect = null;
    const result = fn();
    currentEffect = prev;
    return result;
}
"""
    
    def generate_dom_helpers(self) -> str:
        """Generate DOM helpers."""
        return """
// DOM helpers
function createElement(tag, attrs = {}, children = []) {
    const el = document.createElement(tag);
    
    for (const [key, value] of Object.entries(attrs)) {
        el.setAttribute(key, value);
    }
    
    for (const child of children) {
        if (typeof child === 'string') {
            el.appendChild(document.createTextNode(child));
        } else if (child instanceof Node) {
            el.appendChild(child);
        }
    }
    
    return el;
}

function createFragment(children = []) {
    const fragment = document.createDocumentFragment();
    for (const child of children) {
        if (typeof child === 'string') {
            fragment.appendChild(document.createTextNode(child));
        } else if (child instanceof Node) {
            fragment.appendChild(child);
        }
    }
    return fragment;
}

function bindEvent(el, event, handler) {
    el.addEventListener(event, handler);
    return () => el.removeEventListener(event, handler);
}
"""
    
    def generate_all_helpers(self) -> str:
        """Generate all helper functions."""
        parts = [
            self.generate_signal_helpers(),
            self.generate_reactive_helpers(),
            self.generate_component_helpers(),
            self.generate_dom_helpers(),
        ]
        return '\n'.join(parts)
    
    def generate_style_helpers(self) -> str:
        """Generate style helpers."""
        return """
// Style helpers
function applyStyles(el, styles) {
    for (const [prop, value] of Object.entries(styles)) {
        el.style[prop] = value;
    }
}

function applyClasses(el, classes) {
    if (typeof classes === 'string') {
        el.className = classes;
    } else if (Array.isArray(classes)) {
        el.classList.add(...classes);
    } else if (typeof classes === 'object') {
        for (const [name, active] of Object.entries(classes)) {
            if (active) {
                el.classList.add(name);
            } else {
                el.classList.remove(name);
            }
        }
    }
}
"""
    
    def generate_all(self) -> str:
        """Generate all helper code."""
        return self.generate_all_helpers()
