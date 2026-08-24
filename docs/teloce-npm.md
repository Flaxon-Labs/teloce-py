# Teloce npm compatibility

Teloce-Py targets the same component ideas as Teloce on npm: `.vel` SFCs, reactive state, events, loops, conditions, components, styles, filters, plugins, and runtime mounting.

The Python implementation is intended for teams that want to use existing `.vel` source with a Python backend. Third-party plugins that depend on Node internals must be ported and tested separately.

## Compatibility layers

The original API remains first-class:

```html
<if condition="ready">Ready</if>
<for each="item in items" :key="item.id">{{ item.name }}</for>
<button @click="save">Save</button>
<input :model="email" />
```

The Python implementation also accepts the familiar aliases:

```html
<p v-if="ready">Ready</p>
<li v-for="item in items" :key="item.id">{{ item.name }}</li>
<button v-on:click="save">Save</button>
<input v-model="email" />
```

## Compatibility limits

Source compatibility does not make Node package execution possible inside a
Python process. An npm plugin that only changes `.vel` syntax may be ported to
the Python compiler plugin system. A plugin that starts Node, imports npm
packages, or accesses Node-specific APIs needs a replacement. Verify behavior
with browser tests rather than comparing generated text only.

See [Ecosystem](ecosystem.md) and [npm migration](npm-migration.md) for the
decision and migration guides.
