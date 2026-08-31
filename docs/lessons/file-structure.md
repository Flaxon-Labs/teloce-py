# Optimized Teloce project structure

This structure keeps authored source, Python code, generated assets, tests,
and deployment files separate. It works for Flask, FastAPI, Django, and
Flaxon applications.

```text
my-app/
|-- app.py                         # Python entry point
|-- build.py                       # reproducible Teloce build
|-- teloce.config.json             # shared compiler settings
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- templates/
|   `-- index.html                 # server shell and #app mount
|-- static/
|   |-- js/                        # authored .vel and browser modules
|   |   |-- App.vel
|   |   |-- pages/
|   |   |   |-- Home.vel
|   |   |   `-- Settings.vel
|   |   `-- shared/
|   |       |-- Button.vel
|   |       `-- Card.vel
|   |-- css/                       # optional global CSS only
|   |-- images/
|   `-- vendor/                    # pinned third-party browser assets
|-- api/                           # Python endpoints and schemas
|-- services/                      # database and external integrations
|-- tests/
|   |-- test_api.py
|   |-- test_components.py
|   `-- browser/
|-- dist/                          # generated; deploy or rebuild in CI
`-- docs/
```

## Rules that keep development fast

- Keep each component focused on one screen or reusable visual responsibility.
- Keep `.vel` files under `static/js`; do not edit generated JavaScript.
- Keep secrets and database code in Python, never in browser scripts.
- Put global resets and fonts in `static/css`; keep component styles in the
  component's `<style>` block.
- Import shared components with relative `.vel` imports.
- Keep the first route small and lazy-load infrequently used pages.
- Treat `dist/` as disposable output. Build it in CI unless static hosting
  requires committing it.
- Use the same `teloce.config.json` and build command locally and in CI.

The HTML shell must mount the generated app:

```html
<main id="app"></main>
<script type="module">
  import { mount } from "/static/js/App.js";
  mount("#app");
</script>
```

For an app that exports a router instead, mount that router:

```html
<main id="app"></main>
<script type="module">
  import router from "/static/js/router.js";
  router.mount(document.querySelector("#app"));
</script>
```

Use only one of these mount patterns for an entry point. A component module
exports `mount`; a generated router module exports the router as its default.

## Team ownership

Frontend contributors own `static/js`, component tests, and visual behavior.
Backend contributors own `api`, `services`, database migrations, and Python
tests. Release ownership covers `teloce.config.json`, `build.py`, CI, and
deployment configuration. Review generated output in CI instead of manually
editing it.

Start a new project with `python -m teloce create my-app --template flask`.
The generated project already follows this layout. A default build writes
`static/js/App.vel` to `dist/static/js/App.js`; configure the Python framework
to serve `dist/static` at `/static`, as shown above.
