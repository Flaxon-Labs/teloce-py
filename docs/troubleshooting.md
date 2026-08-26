# Troubleshooting guide

This guide records issues found while building the Flaxon OS simulation and PySeek search engine.

## Blank page or missing UI

Verify the mount target and module path:

```html
<main id="app"></main>
<script type="module">import { mount } from "/assets/static/js/App.js"; mount("#app")</script>
```

Check every generated JavaScript and CSS request in DevTools Network. A wrong output directory or stale service worker can make a valid Python server look blank.

## Text disappears while typing

Do not let a parent native `@input` listener update reactive state on a custom component. The child can be re-rendered and erase the browser value. Use:

```html
<input v-model="localQuery" @input.stop="$emit('suggest', $event.target.value)" />
```

Listen for `@suggest` in the parent. This preserves typing while still supporting suggestions.

## `event.stopPropagation is not a function`

Some runtime versions use `event.detail` for custom events. Native input events can have numeric `detail`, causing a method to receive `0` instead of an event. Prefer the inline `.stop` pattern above or update Teloce-Py to a runtime that distinguishes native and custom events.

## API works but cards are empty or duplicated

Compare the JSON response with the component props. In a loop, pass loop values as interpolated attributes when the runtime cannot preserve loop-scope expressions:

```html
<ResultCard v-for="result in results"
  url="{{ result.url }}" title="{{ result.title }}"
  snippet="{{ result.snippet }}" />
```

Assert that rendered card count equals API result count. Check dynamic `:results` and `:result` bindings in the generated child prop reader.

## Imports, CSS, or routes fail

Resolve imports relative to the importing file and keep filename casing consistent:

```html
<script>import SearchBar from './components/SearchBar.vel'</script>
```

Run `teloce build --out-dir dist`, inspect the generated CSS path, and verify that rewrites do not change `/assets/...` into an unexpected backend route.

## Vercel build fails

Read the first error from `vercel logs`. Common fixes include:

```toml
requires-python = ">=3.11"
dependencies = ["flaxon", "Jinja2>=3.1"]
```

If setuptools reports multiple top-level packages, explicitly declare Python packages in `pyproject.toml`; do not let `public/`, `static/`, or `templates/` be discovered as Python packages.

## Neon returns no results

```bash
curl https://your-app.vercel.app/api/health
curl https://your-app.vercel.app/api/stats
```

The database must be configured, the schema must exist, and a URL must be seeded and crawled. Empty results are different from a database error: empty search returns a successful response with zero results.

## PWA shows an old UI

Increment the service-worker cache name after generated runtime changes, redeploy, and hard-refresh. In DevTools Application, unregister the worker and delete Cache Storage only while diagnosing local stale-cache behavior.

## Bug-report checklist

Include Teloce-Py/Python versions, OS, command, first compiler diagnostic, browser console error, failing network request and response, and a minimal `.vel` file. Never include database URLs, cron secrets, cookies, or private data.
