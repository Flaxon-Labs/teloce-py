# Framework integration

Integration is intentionally thin. Compile the frontend during development or CI, place generated assets under the framework's static directory, and render a mount point.

## Flask

```python
from flask import Flask, render_template

app = Flask(__name__, static_folder="dist/static")

@app.get("/")
def index():
    return render_template("index.html")
```

See [`examples/flask-chat`](../examples/flask-chat).

## FastAPI

Use `StaticFiles` for generated assets and `Jinja2Templates` for the page shell. The `.vel` component communicates with FastAPI through normal JSON endpoints. See [`examples/fastapi-cms`](../examples/fastapi-cms).

## Django

Add the generated directory to `STATICFILES_DIRS`, call `{% load static %}`, and include `<script type="module" src="{% static 'js/App.js' %}"></script>`. See [`examples/django-scanner`](../examples/django-scanner).

## Flaxon

Flaxon is an async ASGI framework with Flask-style decorators. Use its Jinax template integration for the page shell, then load the generated module. See [`examples/flaxon-network`](../examples/flaxon-network).

There is no framework adapter lock-in: any Python server that can serve static files and an HTML mount point can host the output.

## Request and browser responsibilities

The browser component should call routes such as `/api/messages` or
`/api/pages`; it should not connect to a database. The server should validate
input, authenticate the request, authorize the operation, and return a stable
JSON shape. The component should show loading, success, and error states.

## Static paths

Choose one generated output strategy and keep it consistent. If the framework
serves `dist/static`, the HTML must reference `/static/...` through the
framework's URL helper. If a reverse proxy serves assets, use the public asset
base URL and keep the Python route for the HTML shell.

The examples are intentionally independent: each builds its own `.vel` source
and uses in-memory data so the framework boundary is easy to inspect.
