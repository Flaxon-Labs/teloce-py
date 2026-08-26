# Teloce-Py

Author: Aldane Hutchinson

Teloce-Py is a Python-native compiler for Teloce `.vel` Single File Components. It lets a Python team build a reactive browser interface without adding Node, npm, a JavaScript bundler, or a framework-specific frontend stack.

The result is ordinary browser JavaScript and CSS. Your backend remains Flask, FastAPI, Django, Flaxon, or another Python server.

## The problem it solves

Python web applications are excellent at routing, data access, authentication, jobs, and APIs. The difficult part is usually the interactive browser layer: teams add a second toolchain, duplicate templates, or ship large amounts of hand-written DOM code.

Teloce gives that layer a small, inspectable component model:

- one `.vel` file can contain template, browser behavior, and styles;
- the compiler emits self-contained browser modules;
- signals update only the DOM that depends on changed state;
- scoped CSS prevents component styles leaking into the rest of the page;
- the server framework is still responsible for HTTP, sessions, databases, and security;
- development builds can watch files, reload components, emit source maps, and bundle local imports.

## Quick start

```bash
git clone https://github.com/aldanedev-create/teloce-py.git
cd teloce-py
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
```

Create `static/js/App.vel`:

```html
<template>
  <main class="app">
    <h1>{{ title }}</h1>
    <button @click="increment">Clicked {{ count }} times</button>
  </main>
</template>

<script>
export default {
  data() {
    return { title: "Hello from Python", count: 0 };
  },
  methods: {
    increment() { this.count++; }
  }
};
</script>

<style scoped>
.app { max-width: 40rem; margin: 4rem auto; font-family: system-ui; }
</style>
```

Build the project from its root directory:

```bash
python -X utf8 -m teloce.cli.main build --out-dir dist --source-map
```

The generated browser module is written to `dist/static/js/App.js`. Put a mount point in your server template:

```html
<div id="app"></div>
<script type="module">
  import { mount } from "/static/js/App.js";
  mount("#app");
</script>
```

For development, run `teloce dev --port 5173` in a frontend-only project. When using Flask, FastAPI, Django, or Flaxon, run that framework's server and invoke `python -X utf8 -m teloce.cli.main build` as part of the application build step. The `-X utf8` flag keeps the CLI output working in Windows consoles that use a legacy code page.

The complete framework examples are in [`examples/`](examples/), and the walkthroughs are in [`docs/`](docs/).

### Copy-paste Flask app

From a new project directory, install Teloce and Flask:

```bash
python -m pip install teloce-py Flask
python -c "from pathlib import Path; Path('static/js').mkdir(parents=True, exist_ok=True); Path('templates').mkdir(exist_ok=True)"
```

Create `static/js/App.vel`:

```html
<template>
  <main class="app">
    <h1>{{ message }}</h1>
    <button @click="updateMessage">Update</button>
  </main>
</template>

<script>
export default {
  data() { return { message: "Hello from .vel" }; },
  methods: {
    updateMessage() { this.message = "Updated in the browser"; }
  }
};
</script>
```

Create `app.py`:

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
```

Create `templates/index.html`, then build and run:

```html
<!doctype html>
<html><body>
  <div id="app"></div>
  <script type="module">
    import { mount } from "{{ url_for('static', filename='js/App.js') }}";
    mount("#app");
  </script>
</body></html>
```

```bash
python -X utf8 -m teloce.cli.main build --out-dir dist --source-map
python app.py
```

Open `http://127.0.0.1:5000`. The Flask server owns the page route; Teloce owns the browser component.

## What `.vel` supports

Teloce keeps the original Teloce API and adds familiar aliases for users arriving from the npm package. These forms are additive; using `v-if` does not remove support for the original syntax.

| Capability | Original Teloce API | Compatibility aliases |
|---|---|---|
| Conditional rendering | `<if condition="ready">` | `v-if`, `v-else-if`, `v-else` |
| Lists | `<for each="item in items">` | `v-for="item in items"` |
| Events | `@click="save"` | `v-on:click`, `@click.stop.prevent` |
| Attributes/classes | `:class`, `:show` | `v-bind:*`, `v-show`, `v-text`, `v-html` |
| Forms | `:model="email"` | `v-model="email"` |
| Components | local imports and registered components | same component registry contract |
| Styling | `<style scoped>` and CSS modules | same CSS output contract |

TypeScript is not required. Script blocks are JavaScript consumed by the compiler; Python frameworks do not need a TypeScript build step.

## Framework examples

Each example is intentionally small but exercises a real server boundary and a real `.vel` client:

| Example | Backend | Demonstrates |
|---|---|---|
| [`flask-chat`](examples/flask-chat) | Flask | JSON message API, reactive chat UI, form events |
| [`fastapi-cms`](examples/fastapi-cms) | FastAPI | async JSON API, CMS page editing, generated frontend |
| [`django-scanner`](examples/django-scanner) | Django | defensive HTTP security-header scanner and results UI |
| [`flaxon-network`](examples/flaxon-network) | Flaxon | async routes, Jinax templates, WebSocket network events |

These examples use in-memory data so they can be run locally without credentials. Production applications should add authentication, CSRF protection, rate limiting, database transactions, SSRF controls, logging, and deployment-specific configuration.

## Production workflow

Use the compiler as a build step, not as a request-time compiler:

```python
from teloce.build import build_project

result = build_project(
    ".",
    out_dir="dist",
    options={"source_maps": True, "hash_assets": True, "bundle": True},
)
print(result.files)
```

Serve `dist/` from the Python application or a reverse proxy. Keep source maps private when your deployment policy requires it. Run `teloce dev` during development for watching and browser HMR.

The compiler also exposes a standalone runtime for server-rendered HTML. See [`docs/standalone-runtime.md`](docs/standalone-runtime.md).

## VS Code support

The upstream Teloce repository includes a VS Code extension package for `.vel` files. It provides syntax highlighting, diagnostics, autocomplete, hover information, formatting, snippets, symbols, and debugger integration. See the [extension source and installation instructions](https://github.com/aldanedev-create/telonce/tree/main/packages/vscode-extension). It can be installed from the Marketplace when published or from a locally built `.vsix`:

```bash
code --install-extension teloce-vscode.vsix
```

The Python compiler does not replace that editor tooling; it replaces the Node-based compile step for Python projects.

## Compatibility with npm Teloce

The Python compiler is designed for teams that already have `.vel` files from Teloce on npm. Start with [`docs/npm-migration.md`](docs/npm-migration.md), then compile a representative component and compare its behavior in a browser. The compatibility goal covers templates, reactivity, events, conditionals, loops, components, styles, router behavior, filters, plugins, and the public `createApp` runtime API.

Compatibility is a contract to test, not a claim that every third-party npm plugin is automatically portable. Plugins that execute Node-only code must be rewritten as Python compiler plugins or browser-side runtime plugins.

## Documentation

- [Getting started](docs/getting-started.md)
- [`.vel` language and SFC structure](docs/vel-syntax.md)
- [Framework integration](docs/frameworks.md)
- [Production deployment](docs/production.md)
- [PySeek live search-engine showcase](docs/lessons/12-search-engine-showcase.md) — [try it live](https://pyseek.vercel.app)
- [Components, imports, slots, and props](docs/components.md)
- [Plugins, filters, and directives](docs/plugins.md)
- [Router and runtime](docs/router.md)
- [CSS and scoped styles](docs/css.md)
- [VS Code extension](docs/vscode.md)
- [Real-world examples](docs/real-world-examples.md)
- [Contributing](CONTRIBUTING.md)

## Status

This repository is actively developed. Run the test suite before upgrading a production application:

```bash
python -m pytest
```

The package is currently being prepared as beta release `0.2.0b1`. Treat compiler output as a build artifact, pin versions, and use browser end-to-end tests for the flows your application depends on. The beta label is intentional: the compiler, framework examples, and local diagnostics dashboard are usable, but production teams should validate their own browser and deployment matrix.

## License

MIT
