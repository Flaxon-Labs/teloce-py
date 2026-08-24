# Flask

The recommended Flask host compiles once before starting:

```python
from pathlib import Path
from flask import Flask, render_template
from teloce.build import build_project

ROOT = Path(__file__).parent
app = Flask(__name__, static_folder=str(ROOT / "dist" / "static"))

@app.get("/")
def index(): return render_template("index.html")

if __name__ == "__main__":
    build_project(ROOT, options={"dev": True})
    app.run(debug=True)
```

See [Flask chat](../examples/flask-chat).

## Template shell

```html
<!doctype html>
<html lang="en"><body>
  <div id="app"></div>
  <script type="module">
    import { mount } from "{{ url_for('static', filename='js/App.js') }}";
    mount("#app");
  </script>
</body></html>
```

The Flask static folder points at generated output, so the browser receives
`App.js` after `build_project` has run. Flask routes should return JSON for
component requests and should enforce authentication, validation, CSRF policy,
and authorization.

## Development and deployment

Use `python app.py` for the compact example workflow. For a release, run
`teloce build --out-dir dist --hash-assets --bundle` in CI and run Flask behind
a production WSGI server or reverse proxy. Do not use Flask's debug server as
the production server.
