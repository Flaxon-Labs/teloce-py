# Lesson 2: `.vel` building blocks

## State and interpolation

```html
<h2>{{ user.name }}</h2>
<p>{{ items.length }} items</p>
```

State is declared in `data()` and can be changed by methods or event expressions.

## Conditions

Original API:

```html
<if condition="loggedIn">Welcome back</if>
```

Compatible API:

```html
<p v-if="loggedIn">Welcome back</p>
<p v-else>Please sign in</p>
<span v-show="loading">Loading...</span>
```

Use `v-if` when the element should be created and removed. Use `v-show` when it should remain in the DOM and only change visibility.

## Lists and keys

```html
<ul>
  <li v-for="task in tasks" :key="task.id">
    {{ task.title }}
  </li>
</ul>
```

Keys should be stable IDs, not array indexes, when list items can be inserted, removed, or reordered.

## Forms and bindings

```html
<input :model="email" type="email" />
<textarea :model="description"></textarea>
<input :bind:value="searchTerm" />
```

Use `:model` for two-way form state. Use `:bind` when the value flows from state into an attribute or property.

## Events

```html
<button @click="save">Save</button>
<button @click="count++">Add</button>
<form @submit.prevent="submitForm">...</form>
```

Keep complex logic in methods. Short assignments and method calls are useful for simple interactions.

## Filters and expressions

```html
<p>{{ name | capitalize }}</p>
<p>{{ price | currency('USD') }}</p>
<p>{{ tags | join(', ') }}</p>
```

Use filters for presentation. Perform database, authorization, and security decisions in Python, never in a browser expression.

## Components and slots

```html
<template>
  <Panel title="Activity">
    <p slot="default">Recent events appear here.</p>
  </Panel>
</template>
```

Component imports and registration depend on your project build configuration. Keep reusable pieces small: buttons, panels, editors, tables, dialogs, and navigation are good component boundaries.

## CSS

Use `<style scoped>` for component-specific rules and global CSS for tokens, resets, typography, and layout primitives. Prefer CSS variables for themes:

```css
:root { --accent: #55e0c0; --surface: #102c34; }
.button { color: var(--accent); background: var(--surface); }
```

## JavaScript

Use the `<script>` section for state, lifecycle hooks, methods, and browser APIs. For large services such as IndexedDB, media recording, or API clients, put the implementation in regular `.js` modules and call those modules from the component.
