# Production architecture: `.vel`, Python, Jinax, and Flaxon

This lesson assembles the pieces into an application that can be developed
locally, tested in a browser, and deployed behind a Python framework. It uses
Flask because it is the smallest copy-and-paste host. The same generated assets
can be served by Django, FastAPI, or Flaxon; Teloce does not replace the
framework's routing, database, authentication, or security layers.

## The request and build flow

```text
App.vel + imported components
        │
        ├─ Teloce SFC parser and template AST
        ├─ from-scratch JS module-boundary parser
        ├─ CSS parser/scoper and diagnostics
        └─ browser runtime generation
                │
                ├─ dist/static/js/*.js
                ├─ dist/static/css/*.css
                ├─ dist/manifest.json
                └─ optional SSR/static HTML
```

At runtime, Python renders the HTML shell and serves the generated assets.
The generated browser component mounts only into an explicit element such as
`#app`. Reactive updates are scheduled as microtasks and reconciled into the
existing DOM. Keyed loops use `:key` or the original `key` attribute to retain
node identity. Components can be unloaded and HMR records are removed during
unmount.

## Minimal project

Create this layout:

```text
my-app/
├── app.py
├── build.py
├── requirements.txt
├── templates/index.html
└── static/js/App.vel
```

`requirements.txt`:

```text
teloce-py>=0.2.3
Flask>=3.0
```

`build.py`:

```python
from pathlib import Path

from teloce.build import build_project


if __name__ == "__main__":
    result = build_project(
        Path(__file__).parent,
        options={"dev": True, "source_maps": True},
    )
    if result["failed"]:
        raise SystemExit("Teloce build failed: " + "\\n".join(result["errors"]))
    print(f"compiled={result['compiled']} output={ROOT / 'dist'}")
```

`app.py`:

```python
from pathlib import Path

from flask import Flask, jsonify, render_template

from teloce.build import build_project


ROOT = Path(__file__).parent
app = Flask(__name__, static_folder="dist/static", template_folder="dist")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify(ok=True, service="my-app")


if __name__ == "__main__":
    result = build_project(ROOT, options={"dev": True, "source_maps": True})
    if result["failed"]:
        raise SystemExit(result["errors"])
    app.run(debug=True, port=5000)
```

`templates/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Teloce application</title>
  </head>
  <body>
    <main id="app"></main>
    <script type="module">
      import { mount } from "/static/js/App.js";
      mount(document.querySelector("#app"));
    </script>
  </body>
</html>
```

`static/js/App.vel`:

```html
<template>
  <section class="screen" aria-labelledby="title">
    <p class="eyebrow">Python + Teloce</p>
    <h1 id="title">{{ title }}</h1>
    <p>{{ count | number }} requests handled in this session.</p>
    <button type="button" @click="count++">Record request</button>
    <ul>
      <li v-for="item in items" :key="item.id">{{ item.label }}</li>
    </ul>
  </section>
</template>

<script>
export default {
  data() {
    return {
      title: "A real Python application",
      count: 0,
      items: [
        { id: "server", label: "Python owns the server" },
        { id: "ui", label: ".vel owns the interactive UI" },
      ],
    };
  },
};
</script>

<style scoped>
.screen { max-width: 42rem; margin: 4rem auto; padding: 2rem; font: 1rem/1.5 system-ui, sans-serif; }
.eyebrow { color: #6750a4; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
button { border: 0; border-radius: .6rem; padding: .7rem 1rem; background: #6750a4; color: white; cursor: pointer; }
</style>
```

Run it:

```bash
python -m pip install -r requirements.txt
python app.py
```

The HTML must contain the mount target. Importing `App.js` without calling
`mount(...)` is a common reason a browser shows only the static shell.

## Multiple components and imports

Put components beside `App.vel` or in a subdirectory and import them with a
relative `.vel` path:

```html
<script>
import StatusCard from "./components/StatusCard.vel";
export default { components: { StatusCard } };
</script>
```

```html
<template><StatusCard label="Healthy" /></template>
```

The builder resolves the dependency graph, compiles each component once, and
writes the generated import path. `teloce build --lazy-components StatusCard`
emits a dynamic import for that component. Use lazy loading for infrequently
opened screens; do not lazy-load the initial above-the-fold component.

## Jinax/Jinja-compatible SSR

`render_ssr()` translates server-safe Teloce template constructs for a
Jinax/Jinja-compatible environment. Flask can provide its Jinja environment;
Flaxon can provide Jinax directly; Django and FastAPI can pass their own
adapter. Server rendering does not execute browser event handlers or unsafe
JavaScript.

```python
import asyncio

from teloce.ssr import render_ssr


html = asyncio.run(render_ssr(
    '<section><h1>{{ title }}</h1><p v-if="visible">Ready</p></section>',
    {"title": "Server response", "visible": True},
))
```

Use SSR for content that benefits from first-response HTML and SEO. Let the
browser component hydrate or mount into that output for interaction. SSR does
not make authentication or authorization decisions in the browser; those stay
in Python.

## Production build choices

The dependency-free builder is suitable when Teloce owns the generated module
boundaries. For production applications with arbitrary modern JavaScript,
install esbuild separately and let it perform symbol-level tree-shaking,
minification, code splitting, source maps, and target selection:

```bash
npm install --save-dev esbuild
teloce build --bundle --bundler esbuild --hash-assets --report --source-map
```

`--hash-assets` makes cache-safe filenames. Deploy the complete `dist/`
directory, including every lazy chunk, source map selected for release, and
`manifest.json`. Do not copy only `App.js`; imported components and shared
runtime files are part of the output graph.

## Router and lifecycle rules

```html
<template>
  <nav><a href="#/">Home</a><a href="#/settings">Settings</a></nav>
  <section id="view"></section>
</template>
```

The generated router supports hash or history mode, parameters, optional and
wildcard segments, query values, guards, subscriptions, and teardown. A
history-mode deployment must configure the Python host or CDN to return the
HTML shell for client routes. Always retain the unsubscribe function returned
by `router.subscribe`, and call the router's destroy/unmount cleanup when the
owning page is removed.

## Security and operations checklist

- Keep database access, authorization, validation, secrets, and rate limits in
  Python/Flaxon.
- Generated expressions use the constrained evaluator; dynamic code execution
  is not enabled by current generated or standalone runtimes.
- Dynamic `v-html` is sanitized by default. Only set standalone
  `teloce.config.allowRawHtml = true` for trusted, pre-sanitized content.
- Treat `v-html`, third-party plugins, and external URLs as trust boundaries.
- Run `teloce lint`, `teloce build --report`, and the browser tests in CI.
- Set CSP, HTTPS, security headers, request limits, structured logging, and
  error monitoring at the Python deployment boundary.
- For Vercel, keep serverless handlers stateless and use a hosted database or
  queue; the browser build cannot replace persistent backend infrastructure.

## Team workflow

Commit `.vel` sources, Python code, tests, configuration, and lock files.
Usually ignore `dist/` in development and build it in CI; commit it only when
the deployment contract of the repository explicitly requires generated
assets. Review generated diffs when changing compiler versions. A useful pull
request includes the source `.vel`, the Python endpoint contract, a focused
browser test, and the build report.

Before release:

```bash
teloce doctor
teloce lint
python -m pytest -q
python -m build --sdist --wheel
python -m twine check dist/*
```

This workflow demonstrates the role of `.vel` and Flaxon without claiming that
Teloce is a replacement for a full JavaScript/TypeScript compiler or a
backend security layer.
