# Directives

Teloce-Py keeps the original Teloce API. The npm-style `v-*` forms are
additional aliases, not replacements.

## Conditions

Original Teloce API:

```html
<if condition="user">Welcome {{ user.name }}</if>
```

Compatibility API:

```html
<p v-if="user">Welcome {{ user.name }}</p>
<p v-else>Please sign in.</p>
```

The aliases `v-if`, `v-else-if`, and `v-else` can be mixed with normal HTML.

## Lists

Original Teloce API:

```html
<for each="item in items" :key="item.id">{{ item.name }}</for>
```

Compatibility API:

```html
<li v-for="item in items" :key="item.id">{{ item.name }}</li>
```

Use a stable `:key` whenever list items have an identity. The aliases also
support an index when needed:

```html
<li v-for="(item, index) in items">{{ index }}: {{ item.name }}</li>
```

## Events

Original Teloce API:

```html
<button @click="save">Save</button>
<form @submit.prevent="submit">...</form>
```

The `@event` form is the original shorthand. The equivalent npm-style form is:

```html
<button v-on:click="save">Save</button>
<form v-on:submit.prevent="submit">...</form>
```

Supported modifiers include `.prevent`, `.stop`, `.once`, `.self`, and key
modifiers such as `.enter` where applicable.

## Attributes and classes

Original Teloce API:

```html
<div :class="className" :show="visible" :title="title"></div>
```

Compatibility API:

```html
<div v-bind:class="className" v-show="visible" :title="title"></div>
```

The shorthand `:attribute` remains valid and is equivalent to
`v-bind:attribute`.

## Forms

Original Teloce API:

```html
<input :model="email" />
```

Compatibility API:

```html
<input v-model="email" />
```

Both forms keep the component state synchronized with the input value.

## Text and HTML

The compatibility aliases are:

```html
<p v-text="message"></p>
<div v-html="trustedHtml"></div>
```

`v-text` writes escaped text. `v-html` writes HTML and must only receive trusted,
sanitized content. Never pass raw user input to `v-html`.

## Quick reference

| Feature | Original Teloce API | npm-style alias |
|---|---|---|
| Conditional rendering | `<if condition="ready">` | `v-if`, `v-else-if`, `v-else` |
| Lists | `<for each="item in items">` | `v-for="item in items"` |
| Events | `@click="save"` | `v-on:click="save"` |
| Bound attributes | `:class="classes"` | `v-bind:class="classes"` |
| Visibility | `:show="visible"` | `v-show="visible"` |
| Forms | `:model="email"` | `v-model="email"` |
| Text | interpolation or normal text | `v-text="message"` |
| HTML | — | `v-html="trustedHtml"` |
