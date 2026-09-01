# TypeScript extras for real Teloce projects

## Table of contents

1. [Project layout](#project-layout)
2. [Typed API clients](#typed-api-clients)
3. [Typed component utilities](#typed-component-utilities)
4. [Enums and assertions](#enums-and-assertions)
5. [Forms and runtime validation](#forms-and-runtime-validation)
6. [Lazy loading and CI](#lazy-loading-and-ci)

## Project layout

Keep `.vel` components and optional TypeScript utilities in the configured
static source tree. Every Python framework only has to serve the build output.

```text
my-app/
├── app.py
├── teloce.config.json
├── templates/index.html
└── static/js/
    ├── App.vel
    ├── pages/SearchPage.vel
    ├── components/ResultCard.vel
    └── lib/
        ├── api.ts
        └── types.ts
```

Teloce discovers and compiles `.vel` files. It does not compile arbitrary
`.ts` files itself; esbuild or TypeScript transforms those files during the
optional production bundle stage.

## Typed API clients

Use `.ts` modules for reusable browser API clients. Do not put a secret,
database URL, or authorization decision in a browser module.

```ts
// static/js/lib/api.ts
export type Note = { id: string; title: string; body: string };

export async function listNotes(): Promise<Note[]> {
  const response = await fetch("/api/notes");
  if (!response.ok) throw new Error(`Could not load notes (${response.status})`);
  return response.json() as Promise<Note[]>;
}
```

This `.vel` component preserves the runtime import and strips the type-only
import. Bundle before shipping because browsers cannot execute `api.ts`.

```html
<template>
  <section>
    <button type="button" @click="load">Load notes</button>
    <p v-if="error">{{ error }}</p>
    <ul><li v-for="note in notes" :key="note.id">{{ note.title }}</li></ul>
  </section>
</template>

<script lang="ts">
import type { Note } from "../lib/api.ts";
import { listNotes } from "../lib/api.ts";

export default {
  data() { return { notes: [] as Note[], error: "" }; },
  methods: {
    async load(): Promise<void> {
      try { this.notes = await listNotes(); }
      catch (error) { this.error = error instanceof Error ? error.message : "Unknown error"; }
    },
  },
};
</script>

<style scoped>section { display: grid; gap: .8rem; max-width: 48rem; margin: 2rem auto; }</style>
```

## Typed component utilities

Short UI-specific helpers may remain in a `.vel` script. The following alias,
const assertion, generic method annotation, and async method are part of the
tested compatibility surface.

```html
<template>
  <article><h2>{{ summary }}</h2><button type="button" @click="choose('Selected')">Choose</button></article>
</template>

<script lang="ts">
type Choice = { id: number; title: string };
const defaults = { id: 1, title: "First choice" } as const;

export default {
  data(): { choice: Choice } { return { choice: defaults }; },
  computed: { summary(): string { return `${this.choice.id}: ${this.choice.title}`; } },
  methods: {
    async choose<T extends string>(message: T): Promise<void> {
      await Promise.resolve(message);
      this.choice.title = message;
    },
  },
};
</script>

<style scoped>article { border-radius: .75rem; padding: 1rem; background: #f6f7fb; }</style>
```

## Enums and assertions

Teloce lowers simple enums to browser JavaScript objects. Prefer explicit
string values for API and persistence state.

```html
<template><p>{{ message }}</p></template>

<script lang="ts">
enum LoadState { Idle = "idle", Ready = "ready" }
export default { data() { return { message: LoadState.Ready }; } };
</script>

<style scoped>p { color: #166534; }</style>
```

Do not depend on complex numeric reverse mappings, namespace merging, or
decorator transforms in compatibility mode. Use TypeScript's own emitter for
those language features.

## Forms and runtime validation

Types do not validate user input or remote JSON at runtime. Pair a type with a
browser check, then validate again in Python before storing or acting on data.

```html
<template>
  <form @submit.prevent="save">
    <input v-model="email" type="email" aria-label="Email">
    <button>Save</button><p>{{ message }}</p>
  </form>
</template>

<script lang="ts">
export default {
  data(): { email: string; message: string } { return { email: "", message: "" }; },
  methods: {
    save(): void { this.message = this.email.includes("@") ? "Ready to send" : "Enter a valid email"; },
  },
};
</script>

<style scoped>form { display: grid; gap: .6rem; }</style>
```

## Lazy loading and CI

Lazy component imports work at the generated JavaScript module boundary;
esbuild can turn those boundaries into optimized production chunks.

```json
{
  "build": {
    "lazy_components": ["SettingsPage"],
    "shared_runtime": true,
    "minify": true,
    "bundler": "esbuild"
  }
}
```

```bash
npx tsc --noEmit
python -m teloce build --bundle --bundler esbuild --minify --hash-assets --report build-report.json
python -m pytest -q
```

Test a deployed lazy page by direct-loading its URL, navigating away and back,
and checking the browser Network panel. Teloce owns `.vel` edges and the shared
runtime; esbuild owns `.ts` transformation and final chunking.
