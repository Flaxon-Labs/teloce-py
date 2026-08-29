# Optimized Teloce project structure

This structure keeps authored source, Python code, generated assets, tests,
and deployment files separate. It works for Flask, FastAPI, Django, and
Flaxon applications.

```text
my-app/
├── app.py                         # Python entry point
├── build.py                       # reproducible Teloce build
├── teloce.config.json             # shared compiler settings
├── requirements.txt
├── .env.example
├── .gitignore
├── src/
│   └── components/                # authored .vel files only
│       ├── App.vel
│       ├── pages/
│       │   ├── Home.vel
│       │   └── Settings.vel
│       └── shared/
│           ├── Button.vel
│           └── Card.vel
├── templates/
│   └── index.html                  # server shell and #app mount
├── static/
│   ├── css/                        # optional global CSS only
│   ├── images/
│   └── vendor/                     # pinned third-party browser assets
├── api/                            # Python endpoints and schemas
├── services/                       # database and external integrations
├── tests/
│   ├── test_api.py
│   ├── test_components.py
│   └── browser/
├── dist/                           # generated; deploy or rebuild in CI
└── docs/
```

## Rules that keep development fast

- Keep each component focused on one screen or reusable visual responsibility.
- Keep `.vel` files under `src/components`; do not edit generated JavaScript.
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
<script type="module" src="/dist/App.js"></script>
```

For a generated router, mount the router after importing it:

```html
<main id="app"></main>
<script type="module">
  import router from '/dist/router.js';
  router.mount(document.querySelector('#app'));
</script>
```

## Team ownership

Frontend contributors own `src/components`, component tests, and visual
behavior. Backend contributors own `api`, `services`, database migrations, and
Python tests. Release ownership covers `teloce.config.json`, `build.py`, CI,
and deployment configuration. Review generated output in CI rather than
manually editing it.

Start a new project with `teloce create my-app --template flask`, then move
components into this layout gradually. The exact framework shell can remain in
its normal location; only the `.vel` source and generated output need to follow
the compiler's configured paths.
