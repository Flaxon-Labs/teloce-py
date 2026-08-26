# Series: Build a working IDE with `.vel` and Flask

This series builds the small [Vel IDE](https://github.com/aldanedev-create/vel-ide): a browser IDE with a VS Code-style shell, Monaco, multiple imported `.vel` components, a Flask compiler endpoint, and visible compiler diagnostics. It is a copy-pasteable reference project for learning how Teloce-Py and Flask work together.

The project deliberately keeps authored UI and CSS in `.vel` files. The compiler generates browser JavaScript and CSS into `dist/`; generated files are build artifacts and are not edited by hand.

## Part 1 — create the project

```text
vel-ide/
├── app.py
├── build.py
├── requirements.txt
├── templates/index.html
└── static/js/
    ├── App.vel
    └── components/
        ├── ActivityBar.vel
        ├── Explorer.vel
        ├── EditorShell.vel
        ├── ProblemsPanel.vel
        └── PreviewPanel.vel
```

Install the dependencies:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install Flask teloce-py
```

## Part 2 — mount the compiled app

Create `templates/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Vel IDE</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module">
      import { mount } from "/static/js/App.js";
      mount(document.querySelector("#app"));
    </script>
  </body>
</html>
```

The HTML file does not contain the application UI. It only provides the mount point and imports the generated entry module.

## Part 3 — import `.vel` components and keep CSS in `.vel`

Create `static/js/App.vel`:

```html
<script>
import ActivityBar from './components/ActivityBar.vel'
import EditorShell from './components/EditorShell.vel'
import ProblemsPanel from './components/ProblemsPanel.vel'

export default { data() { return { project: 'vel-ide' } } }
</script>
<template>
  <main class="ide">
    <header><strong>{{ project }}</strong><span>Teloce-Py IDE</span></header>
    <section class="workspace">
      <ActivityBar />
      <EditorShell />
      <ProblemsPanel />
    </section>
  </main>
</template>
<style scoped>
.ide { min-height: 100vh; background: #0d1117; color: #e8edf5; font: 14px system-ui; }
header { display: flex; justify-content: space-between; padding: 1rem; background: #151b25; }
.workspace { display: grid; grid-template-columns: 4rem 1fr 18rem; min-height: calc(100vh - 4rem); }
</style>
```

Create `static/js/components/ActivityBar.vel`:

```html
<template><nav class="activity"><button title="Explorer">E</button><button title="Search" @click="window.velIde?.focusSearch()">S</button></nav></template>
<script>export default {}</script>
<style scoped>
.activity { display: grid; align-content: start; gap: .5rem; padding: .75rem; background: #111722; }
button { border: 0; padding: .7rem; background: transparent; color: #8ce3d2; cursor: pointer; }
</style>
```

Create `static/js/components/ProblemsPanel.vel`:

```html
<template><aside class="problems"><strong>PROBLEMS {{ errors }}</strong><p v-if="!errors">No compiler diagnostics.</p><p v-for="item in items">{{ item.message }}</p></aside></template>
<script>
export default {
  data() { return { items: [], errors: 0 } },
  mounted() { this.listener = event => { const data = event.detail || {}; const errors = data.diagnostics?.errors || []; this.items = errors; this.errors = errors.length }; window.addEventListener('velide:diagnostics', this.listener) },
  beforeUnmount() { window.removeEventListener('velide:diagnostics', this.listener) }
}
</script>
<style scoped>
.problems { padding: 1rem; background: #111722; color: #ffb7c8; }
.problems p { color: #9da9ba; font-size: .8rem; }
</style>
```

The other components follow the same rule: template, behavior, and component CSS stay together in one `.vel` file.

## Part 4 — connect Flask to the compiler

Create `app.py`:

```python
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from teloce.compiler import compile as compile_vel

ROOT = Path(__file__).parent
app = Flask(__name__, template_folder=ROOT / "templates", static_folder=ROOT / "dist" / "static")

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/api/compile")
def compile_source():
    payload = request.get_json(silent=True) or {}
    source = payload.get("source", "")
    filename = payload.get("filename", "App.vel")
    if not isinstance(source, str) or len(source) > 250_000:
        return jsonify(ok=False, error="Source must be text under 250 KB."), 400
    try:
        result = compile_vel(source, filename=filename)
    except Exception as error:
        return jsonify(ok=False, diagnostics={"errors": [str(error)]}), 422
    return jsonify(ok=bool(result.get("success")), code=result.get("code", ""), css=result.get("css", ""), diagnostics=result.get("diagnostics", {})), (200 if result.get("success") else 422)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5179, debug=True)
```

Create `build.py`:

```python
from pathlib import Path
from teloce.compiler import build_project

ROOT = Path(__file__).parent
build_project(ROOT, options={"dev": True, "source_maps": True})
print("Vel components compiled")
```

Build and run:

```bash
python build.py
python app.py
```

Open `http://127.0.0.1:5179`.

## Part 5 — add Monaco safely

Monaco should be loaded after the component mounts because the editor host does not exist before mounting. Pin its version and display a failure state. The essential pattern is:

```html
<script>
export default {
  data() { return { editor: null, status: 'Loading editor' } },
  mounted() {
    const script = document.createElement('script')
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.52.2/min/vs/loader.min.js'
    script.onload = () => {
      window.require.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs' } })
      window.require(['vs/editor/editor.main'], () => {
        this.editor = window.monaco.editor.create(document.querySelector('#editor'), { value: '<template></template>', language: 'html', theme: 'vs-dark' })
        this.status = 'Ready'
      })
    }
    script.onerror = () => { this.status = 'Editor failed to load' }
    document.head.appendChild(script)
  },
  beforeUnmount() { this.editor?.dispose() }
}
</script>
```

## Part 6 — test the compiler, not just the appearance

Test a valid component:

```bash
curl -X POST http://127.0.0.1:5179/api/compile \
  -H "content-type: application/json" \
  -d '{"filename":"Card.vel","source":"<template><h1>Hello</h1></template>"}'
```

Test diagnostics intentionally:

```bash
curl -X POST http://127.0.0.1:5179/api/compile \
  -H "content-type: application/json" \
  -d '{"filename":"Broken.vel","source":"<template><div></template>"}'
```

The second request should return HTTP 422 and a diagnostic explaining the missing closing `div`. This is the same failure path used by Vel IDE's Problems panel.

## Part 7 — protect third-party editor DOM from rerenders

Monaco owns a large DOM subtree. If its instance is stored in reactive state, changing a status message can cause a Teloce rerender that replaces Monaco's host. The editor model may still exist while the visible editor is gone. Keep the Monaco instance non-reactive and dispose it when the component unmounts:

```html
<script>
export default {
  mounted() {
    const host = document.querySelector('#editor')
    window.myEditor = window.monaco.editor.create(host, { value: '', language: 'html' })
  },
  beforeUnmount() { window.myEditor?.dispose(); window.myEditor = null }
}
</script>
```

Give the host and its grid row a real height (`height: 100%; min-height: 0`). Test the result by checking that the editor has a non-zero bounding box, typing into Monaco, and compiling the typed source.

## Part 8 — deployment and team workflow

Commit source `.vel` files and build configuration. Either commit `dist/` or run `python build.py` in the deployment build command. On Vercel, use a Python entry point for Flask and ensure the generated static directory matches the Flask `static_folder`.

Teams should review `.vel` source, not generated files; use a consistent Teloce-Py version; run the build and compiler tests in CI; keep Monaco versions pinned; and never expose an unrestricted compile endpoint in a public production IDE without authentication, rate limits, and resource limits.

## What this proves

This project demonstrates that `.vel` can compose a multi-file browser application, own scoped CSS, call browser APIs, mount through ordinary Flask HTML, and communicate with Python through an HTTP compiler endpoint. It does not claim that a small prototype is a complete cloud IDE: persistence, collaboration, sandboxed execution, authentication, project storage, and production isolation are separate features.
