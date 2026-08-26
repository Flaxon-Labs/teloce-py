# How the Teloce Studio prototype was built

Teloce Studio is a prototype no-code workspace built to demonstrate that a visual editor can produce a real Teloce/Flaxon application rather than a static mockup. Its source is maintained as the separate [`teloce-studio`](https://github.com/aldanedev-create/teloce-studio) project.

## The build pipeline

The prototype uses this flow:

```text
visual editor state
        ↓
project model (pages, blocks, theme, assets, resources, workflows)
        ↓
.vel page/component source
        ↓  teloce.build.build_project()
dist/static/*.js and extracted CSS
        ↓
Flask/FastAPI/Django/Flaxon HTML shell
        ↓
browser application
```

The editor stores structured page data, then renders that data into `.vel` entry files. `build_project()` compiles those files. Python remains responsible for APIs, persistence, permissions, jobs, and integrations.

## Product features demonstrated

- JetBrains-inspired workspace with a component palette, canvas, inspector, pages, and backend resources.
- IndexedDB draft autosave and restore, so a browser refresh does not discard a local project.
- Pages, reusable blocks, theme settings, assets, navigation, and workflow metadata in one project model.
- Draft, preview, publish, unpublish, revision, and restore endpoints in the Flaxon backend.
- SQLite-backed local development and a path for replacing the repository with a production database.
- Generated `.vel` files and a normal Python application that can be deployed like any other Flaxon app.

## A small copy-paste version

Create `static/js/App.vel`:

```vel
<template>
  <main class="card">
    <h1>{{ title }}</h1>
    <p>{{ message }}</p>
    <button @click="increment">Clicked {{ clicks }} times</button>
  </main>
</template>
<script>
export default {
  data() { return { title: "My Studio app", message: "Built with .vel", clicks: 0 }; },
  methods: { increment() { this.clicks += 1; } }
}
</script>
<style scoped>
.card { max-width: 40rem; margin: 4rem auto; padding: 2rem; font-family: system-ui; }
button { padding: .6rem 1rem; cursor: pointer; }
</style>
```

Create `templates/index.html`:

```html
<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Studio app</title></head>
  <body><div id="app"></div>
    <script type="module" src="/static/js/App.js"></script>
  </body>
</html>
```

Create `build.py`:

```python
from pathlib import Path
from teloce.build import build_project

if __name__ == "__main__":
    result = build_project(Path(__file__).resolve().parent, options={"dev": True, "source_maps": True})
    print(f"Compiled {result['compiled']} component(s)")
```

Run the build from the project root, then let your Python framework serve `templates/index.html` and `dist/static`.

## Prototype versus production

This proves the architecture and the end-to-end generation path. It does not by itself provide hosted multi-user collaboration, authentication, conflict-free merges, arbitrary server-side code generation, or production security policy. A team product needs those concerns added deliberately: server-side project storage, authorization, audit logs, revision conflict handling, isolated build jobs, validation, and deployment credentials kept on the server.

