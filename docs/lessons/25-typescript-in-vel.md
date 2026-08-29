# TypeScript with `.vel`: copy-paste workflows

Teloce is a Python `.vel` compiler, not a replacement for the TypeScript
compiler. It supports a limited `lang="ts"` compatibility pass for common
type-only syntax. For type checking or advanced TypeScript, use `tsc`, SWC, or
esbuild as an additional build step.

## Option A: simple typed component without a Node toolchain

This works with Teloce's current compatibility pass. Save as
`static/js/App.vel`:

```html
<template>
  <main>
    <h1>{{ greeting }}</h1>
    <button @click="increment">Clicked {{ count }} times</button>
  </main>
</template>

<script lang="ts">
interface CounterState {
  greeting: string;
  count: number;
}

export default {
  data(): CounterState {
    return { greeting: "Teloce + TypeScript", count: 0 };
  },
  methods: {
    increment(): void {
      this.count++;
    },
  },
};
</script>

<style scoped>
main { max-width: 40rem; margin: 4rem auto; font: 1rem/1.5 system-ui, sans-serif; }
button { padding: .7rem 1rem; border: 0; border-radius: .5rem; background: #4338ca; color: white; }
</style>
```

Build it normally:

```bash
teloce build
```

The browser receives JavaScript; the interface and annotations are removed.
This does **not** check whether `CounterState` is correct.

## Option B: full TypeScript checking with `tsc` and esbuild

Use this workflow when your project has generics, decorators, complex types,
or TypeScript shared modules. Install the optional Node tools once:

```bash
npm install --save-dev typescript esbuild
```

Create `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noEmit": true
  },
  "include": ["static/js/**/*.ts"]
}
```

Put typed reusable code in `static/js/lib/format.ts`:

```ts
export type ToolResult = { output: string; changed: boolean };

export function formatJson(source: string, spaces = 2): ToolResult {
  const output = JSON.stringify(JSON.parse(source), null, spaces);
  return { output, changed: output !== source };
}
```

Use it from `static/js/App.vel`:

```html
<template>
  <main>
    <textarea v-model="input" aria-label="JSON input"></textarea>
    <button @click="format">Format</button>
    <pre>{{ output }}</pre>
  </main>
</template>

<script>
import { formatJson } from "./lib/format.ts";

export default {
  data() { return { input: '{"ok":true}', output: "" }; },
  methods: {
    format() {
      try { this.output = formatJson(this.input).output; }
      catch (error) { this.output = error.message; }
    },
  },
};
</script>
```

Check types first, then let Teloce generate component modules and esbuild
bundle them:

```bash
npx tsc --noEmit
teloce build --bundle --bundler esbuild --minify --hash-assets --source-map --report
```

Teloce owns templates, CSS scoping, component imports, and runtime generation.
`tsc` owns TypeScript diagnostics; esbuild owns final JavaScript/TypeScript
transformation, tree-shaking, code splitting, and minification.

## What not to expect from `lang="ts"`

Do not rely on the built-in compatibility pass for full TypeScript features:

- no type checking or editor language service;
- no guarantee for decorators, JSX, declaration merging, or all advanced
  generic syntax;
- no TypeScript package resolution by the Python compiler.

If `teloce build` reports a TypeScript syntax error, use Option B and keep the
complex typed code in `.ts` modules. See the full
[JavaScript and TypeScript tooling guide](../javascript-typescript-tooling.md)
for the exact support boundary.
