# Real-world examples

The examples are deliberately end-to-end rather than isolated template snippets:

- `flask-chat` uses Flask routes and a JSON message API.
- `fastapi-cms` uses async FastAPI routes to list and update CMS pages.
- `django-scanner` demonstrates a defensive, security-header-only URL scanner. It rejects unsupported schemes and must be hardened further before internet-facing use.
- `flaxon-network` uses Flaxon's async route model, Jinax page rendering, and a WebSocket event stream for a small network operations dashboard.

From the repository root, install the framework dependencies listed in the example and build the frontend:

```bash
python -m pip install -e .
python -m pip install -r examples/flask-chat/requirements.txt
python examples/flask-chat/build.py
python examples/flask-chat/app.py
```

Each example directory contains its own README with the equivalent command. The test suite compiles every example `.vel` file so documentation cannot silently drift away from compiler behavior.

## What to study in each example

**Flask chat:** the browser loads messages with `fetch`, posts a new message,
uses a keyed loop, binds an input with `v-model`, and handles form submission.

**FastAPI CMS:** async routes return page data, while the component selects,
edits, and saves a page without making the browser responsible for persistence.

**Django scanner:** the server performs a bounded defensive request and returns
header findings. It demonstrates why validation and SSRF protections belong on
the server.

**Flaxon network:** the app uses async routes, Jinax for the HTML shell, and a
WebSocket endpoint for room events. The inventory is simulated and must not be
confused with an authorized network scanner.

To turn an example into a real application, replace in-memory data with a
database service, add authentication and CSRF protection, validate all input,
add structured logging, and deploy behind a production ASGI/WSGI server.
