# Lesson 15: Create a reusable Teloce plugin

A Teloce plugin is a small package that adds reusable behavior to projects. It can register:

- browser-safe JavaScript filters;
- compiler hooks such as `before_compile` and `after_compile`;
- browser directives;
- Python-side components or application integrations.

Keep secrets, database access, and authorization in Python. A browser plugin is shipped to users and must be treated as public code.

## 1. Create a plugin package

Create `plugins/vel_helpers.py`:

```python
from teloce.plugins.api import Plugin


class VelHelpers(Plugin):
    def __init__(self):
        super().__init__(
            name="vel-helpers",
            version="1.0.0",
            description="Small presentation helpers for .vel applications",
        )

    def install(self, api):
        # This implementation is compiled into the browser bundle.
        api.register_js_filter(
            "initials",
            "value => String(value ?? '').trim().split(/\\s+/).filter(Boolean).map(part => part[0]).join('').toUpperCase()"
        )

        # Hooks run in Python during compilation.
        api.register_hook("after_compile", self.mark_generated_bundle)

    @staticmethod
    def mark_generated_bundle(code):
        return code + "\\n// vel-helpers enabled"
```

The filter is deliberately a presentation helper. It does not fetch data or make security decisions.

## 2. Register the plugin for compilation

In `app.py`, create a registry and pass it to the build options:

```python
from pathlib import Path
from flask import Flask, render_template
from teloce.build import build_project
from teloce.plugins.api import PluginAPI
from teloce.plugins.registry import PluginRegistry
from plugins.vel_helpers import VelHelpers

ROOT = Path(__file__).parent
registry = PluginRegistry()
api = PluginAPI(registry)
registry.set_api(api)
registry.register(VelHelpers())

app = Flask(__name__, template_folder=str(ROOT / "templates"))

@app.get("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    result = build_project(ROOT, options={
        "dev": True,
        "source_maps": True,
        "plugin_registry": registry,
    })
    print(f"Compiled {result['compiled']} components with VelHelpers")
    app.run(debug=True, port=5000)
```

The same registry can be passed to `compile()` for a single component:

```python
from teloce.compiler import compile

result = compile(source, filename="App.vel", plugin_registry=registry)
assert result["success"]
```

## 3. Use the filter in `.vel`

`static/js/App.vel`:

```html
<template>
  <main class="profile">
    <div class="avatar">{{ user.name | initials }}</div>
    <h1>{{ user.name }}</h1>
    <p>{{ user.email }}</p>
  </main>
</template>
<script>
export default {
  data() { return { user: { name: 'Ada Lovelace', email: 'ada@example.test' } } }
}
</script>
<style scoped>
.profile { max-width: 28rem; margin: 4rem auto; text-align: center; font-family: system-ui, sans-serif; }
.avatar { width: 4rem; height: 4rem; display: grid; place-items: center; margin: auto; border-radius: 50%; background: #6556d9; color: white; font-weight: 700; }
</style>
```

The browser receives the generated `initials` function. The Python lambda version of a filter is useful for Python-side tooling, but a browser filter must be registered with `register_js_filter` to appear in generated JavaScript.

## 4. Add a browser directive

Browser directives are registered before the Teloce app mounts. In `templates/index.html`:

```html
<main id="app"></main>
<script>
  window.teloce = window.teloce || {};
  window.teloce.directives = {
    autofocus: {
      render(element) {
        if (!element.disabled && document.activeElement !== element) element.focus();
      }
    }
  };
</script>
<script type="module">
  import { mount } from "/static/js/App.js";
  mount("#app");
</script>
```

Use it in `.vel`:

```html
<input v-autofocus aria-label="Project name" placeholder="Project name" />
```

A directive should be small, deterministic, and safe to run more than once. Do not put passwords, tokens, or server-only logic in a directive.

## 5. Use the built-in plugin classes

For a simple plugin, use the ready-made classes:

```python
from teloce.plugins.directives import DirectivePlugin
from teloce.plugins.filters import FilterPlugin

filters = FilterPlugin(
    name="text-tools",
    filters={"reverse": lambda value: str(value)[::-1]},
)
directives = DirectivePlugin(
    name="focus-tools",
    directives={"focus": {"mounted": lambda element: element.focus()}},
)
registry.register(filters)
registry.register(directives)
```

For browser output, prefer `register_js_filter` and `window.teloce.directives` as shown above. Python callbacks cannot be serialized into browser JavaScript automatically.

## Plugin checklist

- Give the plugin a unique name, version, description, and license.
- Validate options during installation.
- Avoid network access during compilation.
- Keep generated output deterministic.
- Document whether each feature runs in Python or the browser.
- Add a fixture `.vel` file and a compiler test.
- Add a browser test for every directive or interactive feature.
- Test uninstalling the plugin and building without it.
- Never ship secrets in generated JavaScript.
