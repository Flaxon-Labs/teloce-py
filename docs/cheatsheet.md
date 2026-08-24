# Teloce application cheatsheet

This is a practical reference for building a complete Python application with
`.vel` components. The usual division is:

```text
Python framework: routes, APIs, auth, database, HTML shell
Teloce component: browser state, interaction, DOM, component styles
Browser: executes generated JavaScript
```

## 1. Project layout

```text
my-app/
  app.py
  templates/index.html
  static/js/App.vel
  static/js/components/
  static/css/                 # optional global CSS
  requirements.txt
  dist/                       # generated; deploy this directory
```

## 2. Complete component

```html
<template>
  <main class="app">
    <h1>{{ title }}</h1>
    <p v-if="loading">Loading...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <ul v-else>
      <li v-for="task in tasks" :key="task.id">
        <label>
          <input type="checkbox" v-model="task.done" @change="save(task)" />
          <span :class="{ done: task.done }">{{ task.name }}</span>
        </label>
      </li>
    </ul>
    <form @submit.prevent="addTask">
      <input v-model="draft" placeholder="New task" />
      <button :disabled="!draft.trim()">Add</button>
    </form>
  </main>
</template>

<script>
export default {
  data() {
    return { title: "Tasks", tasks: [], draft: "", loading: true, error: "" };
  },
  mounted() { this.load(); },
  computed: {
    remaining() { return this.tasks.filter((task) => !task.done).length; }
  },
  methods: {
    async load() {
      try { this.tasks = await fetch("/api/tasks").then((r) => r.json()); }
      catch (error) { this.error = "The API could not be reached."; }
      finally { this.loading = false; }
    },
    async addTask() {
      const task = await fetch("/api/tasks", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: this.draft }) }).then((r) => r.json());
      this.tasks.push(task); this.draft = "";
    },
    async save(task) { await fetch(`/api/tasks/${task.id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(task) }); }
  }
};
</script>

<style scoped>
.app { max-width: 48rem; margin: 3rem auto; font-family: system-ui; }
.done { text-decoration: line-through; opacity: .6; }
.error { color: #b42318; }
</style>
```

## 3. Template reference

| Need | Original Teloce API | Alias |
|---|---|---|
| Interpolation | `{{ title }}` | `{{ title }}` |
| Condition | `<if condition="ready">...</if>` | `v-if="ready"` |
| Else branch | adjacent conditional content | `v-else-if`, `v-else` |
| List | `<for each="item in items">...</for>` | `v-for="item in items"` |
| Event | `@click="save"` | `v-on:click="save"` |
| Event modifier | `@submit.prevent="save"` | `v-on:submit.prevent="save"` |
| Attribute | `:title="title"` | `v-bind:title="title"` |
| Class | `:class="classes"` | `v-bind:class="classes"` |
| Visibility | `:show="visible"` | `v-show="visible"` |
| Form value | `:model="email"` | `v-model="email"` |
| Text | normal interpolation | `v-text="message"` |
| HTML | not recommended | `v-html="trustedHtml"` |

Original syntax is preserved. You can use either style in the same project.

## 4. Component script API

```js
export default {
  name: "TaskList",
  props: { projectId: { type: String, required: true } },
  data() { return { tasks: [] }; },
  computed: { count() { return this.tasks.length; } },
  watch: { tasks(next) { console.log(next.length); } },
  components: { TaskRow },
  methods: { refresh() {} },
  mounted() {},
  updated() {},
  unmounted() {}
};
```

Use `props` for parent input, `emits` for child-to-parent events, `computed`
for derived values, and `watch` for side effects. Do not place server secrets
in component state.

## 5. Components and imports

```html
<script>
import UserCard from "./components/UserCard.vel";
export default { components: { UserCard } };
</script>
<template><UserCard :user="user" /></template>
```

Use relative local imports. The project build resolves local dependencies and
emits the generated modules. Keep component names consistent with imports.

## 6. Signals

Normal component `data()` is reactive and is the recommended starting point.
For shared browser state, use `createSignal`, `createComputed`, and
`createEffect`; see [Reactivity](reactivity.md).

```js
const count = createSignal(0);
count.set(count() + 1);
const doubled = createComputed(() => count() * 2);
```

## 7. CSS

```html
<style scoped>
.card { padding: 1rem; }
</style>
```

Use scoped styles for component rules and global CSS for resets, fonts, and
design tokens. Never use `v-html` with unsanitized user content.

## 8. Python page shell

```html
<!doctype html>
<html><body>
  <div id="app"></div>
  <script type="module">
    import { mount } from "/static/js/App.js";
    mount("#app");
  </script>
</body></html>
```

## 9. Run and build

Beginner workflow:

```bash
python app.py
```

Development server:

```bash
teloce dev
```

Production build:

```bash
teloce build --out-dir dist --source-map --hash-assets --bundle
```

## 10. Production checklist

- compile during CI, not on every request;
- serve generated assets from a static directory or CDN;
- use stable keys for repeated data;
- authenticate and authorize Python API routes;
- add CSRF protection to state-changing requests;
- sanitize HTML before `v-html`;
- keep source maps private when required;
- run Python and browser tests;
- pin Python and Teloce-Py versions;
- add error monitoring for Python and browser failures.
