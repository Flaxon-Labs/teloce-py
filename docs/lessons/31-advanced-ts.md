# Advanced TypeScript architecture with Teloce

## Table of contents

1. [Production responsibilities](#production-responsibilities)
2. [Layered application design](#layered-application-design)
3. [Python and browser contracts](#python-and-browser-contracts)
4. [Runtime safety](#runtime-safety)
5. [Build modes](#build-modes)
6. [Performance and chunks](#performance-and-chunks)
7. [Release checklist](#release-checklist)
8. [Unsupported features](#unsupported-features)

## Production responsibilities

Use Teloce for `.vel` templates, component options, scoped CSS, local component
imports, and browser-runtime generation. Use TypeScript as optional static
analysis. Use esbuild as the optional final bundler. That keeps each tool's
responsibility clear:

```text
Python API / Flaxon / Flask / FastAPI / Django
                │ JSON over HTTPS
                ▼
       .vel components, CSS, component metadata
                ▼
     generated ESM modules + shared Teloce runtime
                ▼
      tsc diagnostics + esbuild bundles and chunks
                ▼
              browser
```

Python remains responsible for secrets, authentication, authorization,
database access, rate limits, input validation, and business rules. Browser
TypeScript improves feedback to developers; it is not security enforcement.

## Layered application design

Place reusable domain logic in a normal TypeScript module:

```ts
// static/js/domain/tasks.ts
export type Task = { id: string; title: string; done: boolean };

export function visibleTasks(tasks: Task[], mode: "all" | "open" | "done"): Task[] {
  if (mode === "open") return tasks.filter((task) => !task.done);
  if (mode === "done") return tasks.filter((task) => task.done);
  return tasks;
}
```

Make the `.vel` page responsible for UI state and interaction. This complete
example is compiled by the documentation regression test.

```html
<template>
  <main class="tasks">
    <header><h1>{{ title }}</h1><button type="button" @click="toggleMode">Show {{ nextMode }}</button></header>
    <ul><li v-for="task in filtered" :key="task.id">{{ task.title }}</li></ul>
  </main>
</template>

<script lang="ts">
type Mode = "all" | "open" | "done";
type Task = { id: string; title: string; done: boolean };

export default {
  data(): { title: string; mode: Mode; tasks: Task[] } {
    return { title: "Tasks", mode: "all", tasks: [{ id: "welcome", title: "Build with confidence", done: false }] };
  },
  computed: {
    filtered(): Task[] { return this.tasks; },
    nextMode(): string { return this.mode === "all" ? "open" : "all"; },
  },
  methods: {
    toggleMode(): void { this.mode = this.mode === "all" ? "open" : "all"; },
  },
};
</script>

<style scoped>
.tasks { max-width: 52rem; margin: 3rem auto; padding: 1.5rem; border-radius: 1rem; background: #101827; color: #eef2ff; }
header { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
button { border: 1px solid #a5b4fc; border-radius: .5rem; padding: .55rem .8rem; background: transparent; color: inherit; }
</style>
```

For actual filtering, import `visibleTasks` from the `.ts` module and bundle
with esbuild. Keep the simple inline computed value for the dependency-free
Teloce-only path.

## Python and browser contracts

Keep public contracts small and versioned. Python sends JSON; TypeScript
describes the expected shape; runtime code checks failures.

```python
@app.get("/api/tasks")
def list_tasks():
    return {"items": [{"id": "welcome", "title": "Build with confidence", "done": False}]}
```

```ts
export type Task = { id: string; title: string; done: boolean };
export type TaskListResponse = { items: Task[] };

export async function fetchTasks(): Promise<Task[]> {
  const response = await fetch("/api/tasks");
  if (!response.ok) throw new Error("Task API is unavailable");
  const body = await response.json() as TaskListResponse;
  return Array.isArray(body.items) ? body.items : [];
}
```

The assertion helps TypeScript authors but does not validate remote JSON. Use
explicit browser checks when useful and authoritative Python validation always.

## Runtime safety

For larger systems, define contracts in OpenAPI or JSON Schema and generate
browser declarations if useful. Never execute API-provided source code in a
`.vel` component. Never ship database credentials, private API keys, or admin
authorization checks under `static/`.

- Prefer explicit fields instead of `any`.
- Handle failed fetches and malformed response bodies.
- Treat browser identifiers as identifiers, never proof of permission.
- Keep audit logs and privileged decisions on the Python server.

## Build modes

Use readable development output with source maps, then optimized deployment
output. Keep `static_dir` constant so templates mount the same asset URLs.

```json
{
  "compiler": { "source_maps": true, "target": "es2020" },
  "build": {
    "out_dir": "dist", "static_dir": "static", "shared_runtime": true,
    "minify": false, "lazy_components": ["AdminPage", "ReportsPage"]
  }
}
```

```bash
npx tsc --noEmit
python -m teloce build --bundle --bundler esbuild --minify --hash-assets --source-map --report build-report.json
```

Only publish source maps where their source visibility is acceptable for the
application and deployment policy.

## Performance and chunks

Project builds enable `shared_runtime` by default, emitting one runtime file
for every generated component to import. This avoids repeating reactive DOM and
event helpers in every component. Teloce emits configured lazy component
imports; esbuild can turn those ESM boundaries into optimized chunks.

```bash
python -m teloce build --report build-report.json --max-size 50000
```

Review the report, open each lazy route in a clean browser profile, and use the
Network panel to verify unrelated pages are not downloaded. Keep large data in
JSON or an API instead of embedding it in a component script.

## Release checklist

```bash
python -m pytest -q
npx tsc --noEmit
python -m teloce build --bundle --bundler esbuild --minify --hash-assets --report build-report.json
node --check dist/static/js/App.js
```

Also test direct navigation to lazy pages, keyboard behavior, offline/error
states, and the Python API's permission behavior. A successful bundle is only
one part of production readiness.

## Unsupported features

| Do not assume the compatibility pass handles | Use instead |
| --- | --- |
| Full checking, declaration emit, project references | `tsc --noEmit` or a TypeScript build |
| Decorators, JSX/TSX, arbitrary compiler plugins | TypeScript, SWC, or another front-end build step |
| Complex enum semantics and namespace merging | Plain objects/strings or TypeScript transformation first |
| TypeScript path aliases at runtime | Bundler configuration with resolved browser URLs |
| Security validation from static types | Python validation and authorization |

Use Teloce to make `.vel` components productive; use the official TypeScript
ecosystem when the application needs TypeScript's full language guarantees.
