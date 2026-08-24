# Standalone runtime

For server-rendered markup, serve `teloce/runtime/standalone.js` and initialize a root element:

```html
<div id="app">
  <h1>{{ name }}</h1>
  <button @click="count++">{{ count }}</button>
</div>
<script src="/static/teloce-standalone.js"></script>
<script>
  teloce.createApp('#app', { name: 'Python', count: 0 });
</script>
```

The runtime supports the original tags and npm-style aliases, interpolation, events, bindings, loops, conditions, filters, plugins, and component registration. Use compiled `.vel` modules for larger applications so the compiler can optimize imports, styles, and source maps.

## Serving the runtime from Python

Copy or expose the packaged runtime file from your framework's static directory.
For Flask, a route can serve a static directory; for Django, add it to static
files; for FastAPI or Flaxon, mount the directory with the framework's static
file support. The runtime is downloaded by the browser just like any other
JavaScript asset.

## When to use it

Use the standalone runtime for a small server-rendered page, a gradual
migration, or a page where the HTML already comes from Jinja/Jinax. Use compiled
SFC modules for component imports, scoped CSS, source maps, project builds,
and larger applications.

The runtime does not make server-rendered HTML secure automatically. Escape
server values and never use untrusted strings with `v-html`.
