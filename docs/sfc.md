# Single File Components

An SFC groups markup, browser behavior, and styles:

```html
<template>...</template>
<script>export default { ... };</script>
<style scoped>...</style>
```

Only the sections needed by a component are required. The generated output is a browser module that can be mounted from a Python-rendered page.

## Recommended structure

Keep the template declarative, keep browser-only state in the script, and keep
server data access behind an API:

```html
<template>browser view</template>
<script>state, methods, computed values, API calls</script>
<style scoped>component presentation</style>
```

Avoid putting database credentials, private server paths, or authorization
decisions in a script block. Anything compiled into a browser module is public.
