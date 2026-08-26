# Lesson 19: Signals, reactivity, and the browser runtime

Teloce has two related reactivity layers:

1. Component state returned by `data()` is automatically reactive.
2. Explicit signals are small observable values that can be shared by browser modules or runtime helpers.

Use component state for values owned by one `.vel` component. Use signals when independent components, a browser service, or an effect need to observe the same value.

## Component reactivity: the easiest path

Create `static/js/App.vel`:

```html
<template>
  <main class="demo">
    <p class="eyebrow">Teloce reactivity</p>
    <h1>{{ count }} clicks</h1>
    <button @click="increment">Add one</button>
    <button @click="reset">Reset</button>
    <p v-if="count > 0">The component state changed and the DOM updated.</p>
    <p v-else>Click the button to create your first update.</p>
    <ul>
      <li v-for="item in events" :key="item.id">{{ item.label }}</li>
    </ul>
  </main>
</template>

<script>
export default {
  data() {
    return { count: 0, events: [] }
  },
  methods: {
    increment() {
      this.count++
      this.events = [...this.events, { id: this.count, label: `Click ${this.count}` }]
    },
    reset() {
      this.count = 0
      this.events = []
    }
  }
}
</script>

<style scoped>
.demo { min-height: 100vh; display: grid; place-content: center; gap: 1rem; padding: 2rem; background: #0b1020; color: #f4f1ff; font-family: system-ui, sans-serif; }
button { margin-right: .5rem; border: 1px solid #7467b8; border-radius: .6rem; padding: .65rem 1rem; background: #1b1735; color: inherit; cursor: pointer; }
li { margin: .3rem 0; color: #b8aed8; }
</style>
```

`count` and `events` are ordinary JavaScript values from the developer's perspective. Teloce observes assignments made by event handlers, rerenders the component, and updates the affected DOM. Stable `:key` values let the runtime preserve list item identity.

## Explicit signals

Copy the browser runtime into a public static location as part of your build, or expose the packaged runtime using your framework's static-file configuration. Then create `static/js/shared/store.js`:

```js
import { createSignal, createComputed, createEffect } from '/static/teloce/signals.js'

export const online = createSignal(false)
export const status = createComputed(() => online() ? 'Online' : 'Offline')

export const stopStatusLogger = createEffect(() => {
  console.log('Connection status:', status())
})

export function setOnline(value) {
  online.set(Boolean(value))
}
```

Use the store from another browser module:

```js
import { online, status, setOnline } from './shared/store.js'

const label = document.querySelector('#status')
const unsubscribe = status.subscribe(value => { label.textContent = value })
setOnline(true)

// Call unsubscribe() when the page or feature is destroyed.
// stopStatusLogger() stops the effect created by the store.
```

A signal is callable and has useful methods:

```js
const count = createSignal(0)
count()                 // read
count.get()             // read explicitly
count.set(2)            // replace
count.update(value => value + 1)
count.peek()            // read without tracking an effect
const stop = count.subscribe(value => console.log(value))
stop()
```

The tuple form is also supported:

```js
const [name, setName] = createSignal('Ada')
setName('Grace')
console.log(name())
```

## A `.vel` component consuming a signal

For a component that needs a shared signal, import the store in its `<script>` block and copy the current signal value into component state. Subscribe during `mounted` and unsubscribe during `beforeUnmount`:

```html
<script>
import { status } from './shared/store.js'

export default {
  data() { return { status: status() } },
  mounted() {
    this.stopStatus = status.subscribe(value => { this.status = value })
  },
  beforeUnmount() {
    this.stopStatus?.()
  }
}
</script>

<template><p class="status">Server: {{ status }}</p></template>
```

The subscription is a resource. Always remove it when the component unmounts, otherwise a long-running app can retain destroyed components.

## Runtime files and Flask

The Python server does not execute signals. It serves the JavaScript runtime, generated component modules, and HTML shell. A simple Flask setup is:

```python
from pathlib import Path
from flask import Flask, render_template
from teloce.build import build_project

ROOT = Path(__file__).parent
app = Flask(__name__, static_folder=str(ROOT / 'static'))

@app.get('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    build_project(ROOT, options={'dev': True, 'source_maps': True})
    app.run(debug=True, port=5000)
```

In production, serve the runtime from a versioned static path, set cache headers for immutable build assets, and run `teloce build` in CI. Signals are client-side state; passwords, permissions, private records, and authorization decisions must remain in Python.

## Debugging reactivity

If the screen does not update:

- verify the event name and handler name match;
- log the value inside the handler;
- use a stable `:key` in loops;
- check the browser console for generated-module errors;
- confirm the component actually mounted into the HTML element;
- unsubscribe effects and signal listeners during unmount;
- run `teloce lint --strict` and `teloce build --source-map`.

Read [Reactivity](../reactivity.md), [How Teloce-Py works](16-how-teloce-works.md), and [Debugging](../debugging.md) together when diagnosing a larger application.
