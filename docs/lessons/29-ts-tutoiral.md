# TypeScript in `.vel`: a complete practical guide

## Table of contents

1. [What Teloce supports](#what-teloce-supports)
2. [Choosing a workflow](#choosing-a-workflow)
3. [Your first typed component](#your-first-typed-component)
4. [Async methods, props, and state](#async-methods-props-and-state)
5. [Mounting compiled output](#mounting-compiled-output)
6. [Real type checking with `tsc`](#real-type-checking-with-tsc)
7. [Troubleshooting](#troubleshooting)

## What Teloce supports

Teloce compiles templates, component options, scoped CSS, local `.vel` imports,
and browser runtime bindings. Browsers execute JavaScript. In a `<script
lang="ts">` block, Teloce removes a deliberately limited, tested set of
type-only TypeScript syntax before it generates browser JavaScript.

The compatibility pass supports common interfaces and type aliases, type-only
imports, ordinary parameter/return/variable annotations, simple assertions,
and simple enums. It is useful when a Python team wants readable types without
requiring a Node toolchain for its first `.vel` build.

It is not a type checker. Teloce does not prove that a value satisfies an
interface, resolve every TypeScript package, emit declarations, or provide the
TypeScript language service. Use `tsc` for those jobs. This is intentional:
Flask, FastAPI, Django, and Flaxon projects can keep `python app.py`, while
projects needing full TypeScript opt into the normal TypeScript toolchain.

## Choosing a workflow

| Need | Use |
| --- | --- |
| A small component with common annotations | `lang="ts"` and `python -m teloce build` |
| Strict diagnostics in local development and CI | `npx tsc --noEmit` before Teloce build |
| Shared `.ts` utility modules | `tsc` plus esbuild bundling |
| Decorators, JSX/TSX, complex type-level code | TypeScript or SWC before browser delivery |
| No Node dependency | Plain JavaScript or Teloce's limited TS compatibility pass |

## Your first typed component

Save this as `static/js/pages/Counter.vel`. It is complete, copy-pasteable,
and tested automatically with the other `.vel` examples in this lesson.

```html
<template>
  <main class="counter">
    <p class="eyebrow">Teloce + TypeScript</p>
    <h1>{{ title }}</h1>
    <p>You clicked {{ count }} times.</p>
    <button type="button" @click="increment">Add one</button>
  </main>
</template>

<script lang="ts">
interface CounterState {
  title: string;
  count: number;
}

export default {
  data(): CounterState {
    return { title: "Typed without friction", count: 0 };
  },
  methods: {
    increment(): void { this.count++; },
  },
};
</script>

<style scoped>
.counter { max-width: 42rem; margin: 4rem auto; font: 1rem/1.5 system-ui, sans-serif; }
.eyebrow { color: #635bff; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
button { border: 0; border-radius: .6rem; padding: .7rem 1rem; background: #312e81; color: white; cursor: pointer; }
</style>
```

After compilation the browser receives JavaScript. `CounterState`, `string`,
`number`, and `void` are authoring-time annotations and are removed. The
template stays reactive because Teloce generates the same runtime bindings as
an ordinary JavaScript component.

## Async methods, props, and state

Use normal runtime prop declarations for browser validation; use TypeScript
annotations to make intent clear to authors. Keep `async` before every method,
lifecycle hook, or watcher that contains `await`.

```html
<template>
  <section class="profile-card">
    <h2>{{ user.name }}</h2>
    <p>{{ status }}</p>
    <button type="button" @click="refresh">Refresh profile</button>
  </section>
</template>

<script lang="ts">
interface User { id: number; name: string; }
type ProfileState = { user: User; status: string };

export default {
  props: { initialName: { type: String, default: "Ada" } },
  data(): ProfileState {
    return { user: { id: 1, name: this.initialName }, status: "Ready" };
  },
  methods: {
    async refresh(): Promise<void> {
      this.status = "Refreshing…";
      await Promise.resolve();
      this.status = `Updated for ${this.user.name}`;
    },
  },
};
</script>

<style scoped>.profile-card { padding: 1rem; border: 1px solid #d9dce8; border-radius: .75rem; }</style>
```

The generated `refresh` method remains `async`. This is a compiler regression
case because removing `async` would make any `await` invalid browser code.

## Mounting compiled output

Build from the project root, then run the usual Python server:

```bash
python -m teloce build
python app.py
```

The HTML page must mount the generated module. The URL below assumes the
standard `static_dir: "static"` configuration.

```html
<div id="app"></div>
<script type="module">
  import Counter from "/static/js/pages/Counter.js";
  Counter.mount(document.querySelector("#app"));
</script>
```

Production project builds enable `shared_runtime` by default. Every generated
component imports one runtime file rather than embedding reactive DOM/event
helpers repeatedly. See [the shared runtime lesson](shared%20runtime.md).

## Real type checking with `tsc`

Install optional tooling only when the application needs full TypeScript:

```bash
npm install --save-dev typescript esbuild
```

```json
{
  "compilerOptions": {
    "target": "ES2022", "module": "ESNext", "moduleResolution": "Bundler",
    "strict": true, "noEmit": true
  },
  "include": ["static/js/**/*.ts"]
}
```

Run separate, understandable jobs:

```bash
npx tsc --noEmit
python -m teloce build --bundle --bundler esbuild --minify --hash-assets --source-map
```

`tsc` owns type diagnostics. Teloce owns `.vel` templates and scoped CSS.
esbuild owns final TypeScript transformation, bundling, tree-shaking, splitting,
and minification. A successful Teloce build alone is not evidence that complex
types are correct.

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| `await is only valid in async functions` | Put `async` before the method/hook/watcher that awaits, then rebuild. |
| A browser cannot load a `.ts` import | Browsers cannot execute TypeScript; bundle it with esbuild/SWC/TypeScript. |
| A decorator, JSX, or advanced generic fails | It is outside the compatibility pass; use the full TypeScript build stage. |
| Types do not catch an error | Add `npx tsc --noEmit` locally and in CI. |
| Output is too large | Keep `shared_runtime` and `minify` enabled; bundle with esbuild. |

Read [JavaScript and TypeScript tooling](../javascript-typescript-tooling.md)
for the complete support boundary and [the shorter TypeScript lesson](25-typescript-in-vel.md)
for a quick start.
