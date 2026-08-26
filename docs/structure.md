# Teloce project structure

This is the recommended layout for a Teloce application. It keeps Python server code, Jinax/Jinja templates, `.vel` source, and generated browser assets easy to understand.

```text
my-app/
├── pyproject.toml              # Python package and tool configuration
├── requirements.txt             # deploy/runtime dependencies
├── app.py                       # Flask, FastAPI, Django, or Flaxon entry point
├── build.py                     # repeatable Teloce build command
├── templates/                   # server-rendered HTML shells
│   ├── index.html
│   └── admin.html
├── static/
│   ├── js/                      # source .vel files and optional JS modules
│   │   ├── App.vel
│   │   └── admin/Admin.vel
│   └── css/                     # ordinary global CSS, if needed
├── dist/                        # generated output; do not edit by hand
│   └── static/js/*.js
├── tests/                       # Python and browser-facing tests
└── docs/
```

## What belongs where

- `templates/` contains the HTML document, server-side metadata, navigation, and the mount element such as `<div id="app"></div>`.
- `static/js/*.vel` contains interactive components. The compiler turns each `.vel` entry point into browser JavaScript and extracts its styles.
- `static/js/components/` is a useful home for imported child components. Keep one public entry component per page.
- `dist/` is build output. Deploy it with the application, but never use it as the source of truth.
- Python routes, database access, authentication, background jobs, and secrets remain in Python. A `.vel` component calls those capabilities through HTTP or WebSocket APIs; it does not replace server authorization.

## Framework mapping

| Server | HTML shell | Browser asset route | Local command |
| --- | --- | --- | --- |
| Flask | `render_template()` | Flask `static` | `python app.py` |
| FastAPI | `Jinja2Templates` | `StaticFiles` | `python app.py` |
| Django | `render()` | `STATIC_URL`/WhiteNoise or a web server | `python manage.py runserver` |
| Flaxon | Jinax `request.render()` | Flaxon static route or asset handler | `python build.py`, then `flaxon run app:app` |

The compiler is framework-neutral because it emits browser assets. The server only needs to serve the generated files and render an HTML page that imports them.

## Multiple pages

Use one HTML shell and one `.vel` entry point per page when pages have separate responsibilities:

```text
templates/index.html       -> /static/js/App.js       -> static/js/App.vel
templates/admin.html       -> /static/js/admin/Admin.js -> static/js/admin/Admin.vel
```

The `.vel` files can share components with relative imports. Each HTML file gets its own mount element and imports only its entry module. See [Multiple HTML pages](multiple-html-pages.md).

## Generated files and source control

Run `python build.py` in development and CI. Keep source `.vel` files and build configuration in Git. Whether `dist/` is committed is a deployment choice: commit it for a simple static-host deployment, or generate it in CI for reproducible builds. Never commit secrets, local databases, `__pycache__/`, or browser-local IndexedDB data.

