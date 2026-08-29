# Build a lazy-loaded developer toolbox

This lesson uses the same architecture as the Developer Toolbox: one real
`.vel` application shell, small browser utility modules, and `import()` to
load a utility only when the user selects it. Do not create placeholder pages
or components merely to make a project look larger. Every file below is used.

## Project layout

```text
toolbox/
├── app.py
├── build.py
├── templates/index.html
└── static/js/
    ├── App.vel
    └── tools/
        ├── json.js
        └── uuid.js
```

## 1. Add real lazy utility modules

`static/js/tools/json.js`:

```js
export function run(source, indent = 2) {
  return JSON.stringify(JSON.parse(source), null, Number(indent));
}
```

`static/js/tools/uuid.js`:

```js
export function run() {
  if (!crypto.randomUUID) throw new Error("Your browser does not support crypto.randomUUID().");
  return crypto.randomUUID();
}
```

These files contain no component UI. They are small, testable browser modules.
They are fetched only after the chosen tool is opened.

## 2. Create the application shell

Copy this into `static/js/App.vel`:

```html
<template>
  <main class="toolbox">
    <nav aria-label="Tools">
      <button :class="tool === 'json' ? 'active' : ''" @click="selectTool('json')">JSON</button>
      <button :class="tool === 'uuid' ? 'active' : ''" @click="selectTool('uuid')">UUID</button>
    </nav>

    <section>
      <h1>{{ title }}</h1>
      <label>
        Input
        <if condition="tool !== 'uuid'"><textarea v-model="input"></textarea></if>
      </label>
      <button @click="runTool" :disabled="loading">{{ loading ? 'Loading…' : 'Run tool' }}</button>
      <output>{{ output }}</output>
      <p role="status">{{ message }}</p>
    </section>
  </main>
</template>

<script>
export default {
  data() {
    return {
      tool: "json",
      title: "JSON formatter",
      input: '{"hello":"Teloce"}',
      output: "",
      message: "Choose a tool and run it.",
      loading: false,
      requestId: 0,
    };
  },
  methods: {
    selectTool(name) {
      this.tool = name;
      this.title = name === "json" ? "JSON formatter" : "UUID generator";
      this.output = "";
      this.message = "Ready.";
    },
    async runTool() {
      const loaders = {
        json: () => import("./tools/json.js"),
        uuid: () => import("./tools/uuid.js"),
      };
      const currentRequest = ++this.requestId;
      this.loading = true;
      try {
        const module = await loaders[this.tool]();
        const result = module.run(this.input, 2);
        if (currentRequest !== this.requestId) return;
        this.output = result;
        this.message = "Processed locally.";
      } catch (error) {
        if (currentRequest !== this.requestId) return;
        this.output = "";
        this.message = error.message || "The tool could not process this input.";
      } finally {
        if (currentRequest === this.requestId) this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.toolbox { display: grid; grid-template-columns: 12rem 1fr; min-height: 100vh; font: 1rem/1.5 system-ui, sans-serif; }
nav { padding: 1rem; background: #111827; } nav button { display: block; width: 100%; margin: .4rem 0; padding: .7rem; border: 0; border-radius: .4rem; color: white; background: transparent; text-align: left; }
nav button.active { background: #374151; } section { max-width: 52rem; padding: 2rem; } textarea, output { display: block; width: 100%; min-height: 10rem; margin: .6rem 0 1rem; padding: .8rem; border: 1px solid #cbd5e1; border-radius: .5rem; white-space: pre-wrap; }
@media (max-width: 40rem) { .toolbox { grid-template-columns: 1fr; } nav { display: flex; gap: .5rem; } nav button { margin: 0; } }
</style>
```

`requestId` prevents a slow earlier import/result from overwriting the latest
selection. This matters when a user changes tools quickly.

## 3. Mount the compiled application

`templates/index.html`:

```html
<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Toolbox</title></head>
  <body>
    <div id="app"></div>
    <script type="module">
      import { mount } from "/static/js/App.js";
      mount(document.querySelector("#app"));
    </script>
  </body>
</html>
```

The mount call is required. If the browser receives `App.js` but the page is
blank, first verify that the HTML contains `#app` and calls `mount(...)`.

## 4. Build and serve with Flask

`app.py`:

```python
from pathlib import Path

from flask import Flask, render_template
from teloce.build import build_project

ROOT = Path(__file__).parent
build_project(ROOT, options={"dev": True, "clean": True})
app = Flask(__name__, static_folder="dist/static", template_folder="templates")

@app.get("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
```

Install and run:

```bash
python -m pip install teloce-py Flask
python app.py
```

For a production build, keep the entire generated `dist/` directory. Dynamic
imports are separate files: deploying only `App.js` makes selected tools fail
with a module 404.

```bash
teloce build --hash-assets --report
```

Use `--bundle --bundler esbuild --minify` when esbuild is installed and you
need production code splitting and whole-program optimization.
