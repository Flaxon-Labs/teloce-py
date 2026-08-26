# Lesson 16: How Teloce-Py works under the hood

This lesson explains the complete path from a `.vel` file to a working browser application. Understanding the boundary between Python and the browser makes debugging and production deployment much easier.

## The complete pipeline

```text
App.vel / components/*.vel
        |
        v
project discovery -> SFC parser -> AST -> transforms
        |
        v
JavaScript + scoped CSS + source maps
        |
        v
Flask / FastAPI / Django / Flaxon serves HTML and static files
        |
        v
browser mounts the generated component and runs the runtime
```

Teloce-Py is a compiler and browser-runtime tool. It does not turn Python into browser code. Python builds assets and serves requests; generated JavaScript owns reactive DOM behavior in the browser.

## What happens during discovery

`build_project()` starts at the project root and finds the source directories, `.vel` files, templates, and static assets. A normal project looks like this:

```text
my-app/
├── app.py
├── templates/index.html
└── static/js/
    ├── App.vel
    └── components/Counter.vel
```

The compiler keeps the relative component path when it writes generated modules. This makes local component imports predictable and lets teams organize components by feature.

## What the SFC parser does

A `.vel` file is divided into sections:

```html
<template>...</template>
<script>...</script>
<style scoped>...</style>
```

The parser records the source locations, then produces an intermediate representation. Template nodes include elements, attributes, text, interpolations, directives, and component tags. The script becomes component options such as `data`, `methods`, `mounted`, and `beforeUnmount`. Scoped CSS is transformed so selectors are limited to that component.

## What the runtime does

At mount time, the generated module:

1. creates component state from `data()`;
2. renders the template into the mount element;
3. evaluates interpolations such as `{{ title }}`;
4. attaches event handlers such as `@click`;
5. evaluates conditions, loops, bindings, and components;
6. rerenders the affected component when reactive state changes;
7. calls lifecycle hooks and removes listeners during unmount.

Signals are useful when several pieces of code need to observe the same value. Ordinary component state is enough for local UI state. Use the runtime signal APIs documented in [Reactivity](../reactivity.md) for shared or externally updated state.

## The Python/browser boundary

This is the most important production rule:

```text
Python process: database, secrets, authentication, APIs, jobs, files
Browser runtime: DOM, events, animations, local state, IndexedDB
```

Browser code cannot directly call a Python function or access a Python database object. It calls a Flask/FastAPI/Django/Flaxon endpoint with `fetch()` or a WebSocket. The server validates the request and returns JSON or HTML.

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.post('/api/greeting')
def greeting():
    name = (request.json or {}).get('name', 'developer').strip()[:80]
    return jsonify({'message': f'Hello, {name}'})
```

```html
<script>
async function greet(name) {
  const response = await fetch('/api/greeting', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  })
  if (!response.ok) throw new Error('Greeting request failed')
  return response.json()
}
</script>
```

## Router and mounting

The router is browser-side navigation. The Python framework still serves the HTML shell and assets. For a generated router, mount an element, not a selector string:

```html
<div id="app"></div>
<script type="module">
  import router from '/static/js/router.js'
  router.mount(document.querySelector('#app'))
</script>
```

The router reads the hash or history URL, selects a component, unmounts the previous view, and mounts the new one. A server deployment must still return the shell for the entry URL. Hash mode is the simplest option on serverless hosting because every route remains in one document URL.

## Build-time versus runtime errors

Compiler errors happen while parsing or generating a `.vel` file and should include the source file and line. Runtime errors happen after the browser loads the generated module. Check both layers:

```bash
teloce doctor --verbose
teloce lint --strict
teloce build --out-dir dist --source-map
```

Then open browser DevTools and check the generated module URL and source map. See [Debugging](../debugging.md) for the dashboard and [Troubleshooting](../troubleshooting.md) for common mount, import, and template failures.

## Production mental model

Build once in CI, serve the generated assets with cache headers, keep secrets on the Python side, validate every API request, and test the browser at the mount point. Teloce makes the UI portable; it does not remove the normal responsibilities of a production web application.
