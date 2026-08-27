# Lesson 1: your first `.vel` file

## 1. Create a project

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install teloce-py
mkdir static/js/components
```

Create `static/js/components/Welcome.vel`:

```html
<template>
  <section class="card">
    <h1>{{ title }}</h1>
    <p>{{ message }}</p>
    <button @click="message = 'The component is interactive.'">Test interaction</button>
  </section>
</template>

<style scoped>
.card { max-width: 30rem; padding: 2rem; border-radius: 1rem; }
</style>

<script>
export default {
  data() {
    return { title: "Hello from Teloce", message: "Edit a .vel file and compile it." };
  }
};
</script>
```

The compiler reads the three sections as one component. The template becomes DOM operations, the style is scoped to the component, and the script supplies state and methods.

## 2. Compile it

```bash
teloce compile static/js/components/Welcome.vel --output public/js/components/Welcome.js
```

For a project with many components, use the project build command described in [the CLI guide](../cli.md). Generated JavaScript belongs in your build output; do not edit generated files by hand.

## 3. Mount it

```html
<div id="welcome"></div>
<script type="module">
  import { mount } from "/static/js/components/Welcome.js";
  mount("#welcome");
</script>
```

The browser needs to receive the compiled JavaScript through the normal static-file system of your Python framework.

## 4. What makes `.vel` productive

- Template, behavior, and component styles live together.
- State changes update the rendered UI.
- Events use readable HTML attributes such as `@click`.
- Lists, conditions, bindings, slots, and components are expressed near the markup.
- The same component can be mounted by Flask, FastAPI, Django, Flaxon, or a plain static server.

The result is not a new Python web framework. It is a focused UI compilation layer for Python applications.
