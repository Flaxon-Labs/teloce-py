# Lesson 14: Build a demo UI framework with `.vel`

Yes, `.vel` can be used to create a small demo component framework. The result is not a replacement for Flask, Django, FastAPI, or Flaxon. It is a reusable browser UI layer with component contracts, shared styling, state, events, and composition.

## What this demo framework contains

```text
App.vel
  -> DemoShell.vel
       -> UiButton.vel
       -> UiCard.vel
       -> UiModal.vel
```

Each component owns its template, props, events, and optional scoped CSS. A real framework would add accessibility rules, tests, versioning, documentation, and a published component package.

## 1. Create a reusable button

`static/js/components/UiButton.vel`:

```html
<template>
  <button class="ui-button" :class="'ui-button--' + (variant || 'primary')" :disabled="disabled" @click="$emit('press', $event)">
    <slot></slot>
  </button>
</template>
<script>
export default { props: { variant: String, disabled: Boolean } }
</script>
<style scoped>
.ui-button { border: 0; border-radius: .7rem; padding: .7rem 1rem; color: white; cursor: pointer; font: inherit; }
.ui-button--primary { background: #5d55d9; }
.ui-button--quiet { background: #27304b; }
.ui-button:disabled { cursor: not-allowed; opacity: .5; }
</style>
```

## 2. Create a card component

`static/js/components/UiCard.vel`:

```html
<template>
  <section class="ui-card">
    <header v-if="title"><h2>{{ title }}</h2><small v-if="tag">{{ tag }}</small></header>
    <div class="ui-card__body"><slot></slot></div>
  </section>
</template>
<script>
export default { props: { title: String, tag: String } }
</script>
<style scoped>
.ui-card { border: 1px solid #293452; border-radius: 1rem; background: #11182b; color: #eef2ff; box-shadow: 0 .8rem 2rem #05081380; }
.ui-card header { display: flex; justify-content: space-between; gap: 1rem; padding: 1rem 1.1rem 0; }
.ui-card h2 { margin: 0; font-size: 1.05rem; }
.ui-card small { color: #8dded0; }
.ui-card__body { padding: 1.1rem; }
</style>
```

## 3. Create a modal component

`static/js/components/UiModal.vel`:

```html
<template>
  <div v-if="open" class="backdrop" role="presentation" @click.self="$emit('close')">
    <section class="modal" role="dialog" aria-modal="true" :aria-label="title">
      <header><h2>{{ title }}</h2><button aria-label="Close" @click="$emit('close')">×</button></header>
      <div><slot></slot></div>
    </section>
  </div>
</template>
<script>
export default { props: { open: Boolean, title: String } }
</script>
<style scoped>
.backdrop { position: fixed; inset: 0; display: grid; place-items: center; padding: 1rem; background: #030612aa; z-index: 10; }
.modal { width: min(32rem, 100%); border: 1px solid #56638d; border-radius: 1rem; padding: 1.1rem; background: #131b31; color: #eef2ff; }
.modal header { display: flex; justify-content: space-between; align-items: center; }
.modal button { border: 0; background: transparent; color: inherit; font-size: 1.5rem; cursor: pointer; }
</style>
```

## 4. Compose the framework in an application

`static/js/DemoShell.vel`:

```html
<script>
import UiButton from './components/UiButton.vel'
import UiCard from './components/UiCard.vel'
import UiModal from './components/UiModal.vel'

export default {
  components: { UiButton, UiCard, UiModal },
  data() { return { modalOpen: false, clicks: 0 } },
  methods: { addClick() { this.clicks++ }, closeModal() { this.modalOpen = false } }
}
</script>
<template>
  <main class="demo-shell">
    <nav><strong>MiniVel UI</strong><span>Demo framework</span></nav>
    <h1>Reusable `.vel` components</h1>
    <p>One component system, composed into an application.</p>
    <div class="grid">
      <UiCard title="Buttons" tag="ui-button">
        <UiButton @press="addClick">Clicked {{ clicks }} times</UiButton>
        <UiButton variant="quiet" @press="modalOpen = true">Open modal</UiButton>
      </UiCard>
      <UiCard title="Framework contract" tag="props + events + slots">
        <ul><li>Props configure components.</li><li>Events send actions upward.</li><li>Slots provide page content.</li></ul>
      </UiCard>
    </div>
    <UiModal :open="modalOpen" title="MiniVel modal" @close="closeModal">
      <p>This modal is another imported `.vel` component.</p>
      <UiButton variant="quiet" @press="closeModal">Close</UiButton>
    </UiModal>
  </main>
</template>
<style scoped>
.demo-shell { min-height: 100vh; padding: 2rem; background: #080d1b; color: #eef2ff; font-family: system-ui, sans-serif; }
nav { display: flex; justify-content: space-between; max-width: 64rem; margin: auto; color: #9aa8cf; }
.demo-shell > h1, .demo-shell > p, .grid { max-width: 64rem; margin-left: auto; margin-right: auto; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; margin-top: 2rem; }
.grid .ui-button + .ui-button { margin-left: .5rem; }
@media (max-width: 700px) { .demo-shell { padding: 1rem; } .grid { grid-template-columns: 1fr; } }
</style>
```

Create `static/js/App.vel`:

```html
<script>import DemoShell from './DemoShell.vel'; export default { components: { DemoShell } }</script>
<template><DemoShell /></template>
```

## 5. Run it with Python

Use the standard `python app.py` host:

```python
from pathlib import Path
from flask import Flask, render_template
from teloce.build import build_project

ROOT = Path(__file__).parent
app = Flask(__name__, template_folder=str(ROOT / 'templates'))

@app.get('/')
def home(): return render_template('index.html')

if __name__ == '__main__':
    result = build_project(ROOT, options={'dev': True, 'source_maps': True})
    print(f"Compiled {result['compiled']} .vel components")
    app.run(debug=True, port=5000)
```

`templates/index.html`:

```html
<main id="app"></main>
<script type="module">import { mount } from '/static/js/App.js'; mount('#app')</script>
```

Run:

```bash
python app.py
```

## What makes this a framework?

The framework-like value comes from repeatable contracts, not the number of files:

- `UiButton` accepts props and emits a press event;
- `UiCard` and `UiModal` expose slots;
- components are imported instead of copied;
- CSS is owned by components and can share design tokens;
- the application shell composes components without knowing their internal markup.

For a production component framework, add keyboard and focus tests, visual regression tests, stable public prop/event names, semantic versioning, changelogs, TypeScript declarations if desired, and a package distribution strategy. `.vel` can remain the authoring format while Python and Flaxon continue to provide the application backend.
