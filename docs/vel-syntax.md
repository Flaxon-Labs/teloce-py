# `.vel` syntax

A Single File Component has up to three sections:

```html
<template>...</template>
<script>export default { ... };</script>
<style scoped>...</style>
```

The original Teloce forms remain supported:

```html
<if condition="user">Welcome {{ user.name }}</if>
<for each="item in items" :key="item.id">{{ item.name }}</for>
<button @click.prevent="save">Save</button>
<input :model="email">
```

npm-style aliases are also supported:

```html
<p v-if="ready">Ready</p>
<li v-for="item in items" :key="item.id">{{ item.name }}</li>
<input v-model="email">
<button v-on:click="save">Save</button>
```

Component scripts use the Teloce object API: `data`, `methods`, `computed`, `watch`, lifecycle hooks, `props`, and `emits`. JavaScript is the component language. TypeScript is deliberately not required by the Python compiler.

Use `:class`, `v-bind:class`, object class maps, and scoped styles for presentation. Use `v-text` for escaped text and reserve `v-html` for trusted, sanitized HTML.
