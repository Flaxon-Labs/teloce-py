# Jinax and `.vel` together

Jinax and Teloce solve different layers of the same page:

- Jinax renders the initial HTML document on the server.
- `.vel` compiles interactive browser behavior into JavaScript.
- Python APIs remain the trusted boundary for data and authorization.

## Flaxon example

`app.py`:

```python
from pathlib import Path

from flaxon import Flaxon
from flaxon.jinax import Jinax
from teloce.build import build_project

ROOT = Path(__file__).resolve().parent
app = Flaxon("jinax-vel", debug=True)
app.use_templates(Jinax(str(ROOT / "templates"), auto_reload=True))

@app.get("/")
async def home(request):
    return await request.render("index.html", {"title": "Jinax + Teloce"})

@app.get("/api/health")
async def health():
    return {"ok": True}

if __name__ == "__main__":
    result = build_project(ROOT, options={"dev": True, "source_maps": True})
    print(f"Compiled {result['compiled']} component(s)")
```

`templates/index.html`:

```html
<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>{{ title }}</title></head>
  <body>
    <div id="app"></div>
    <script type="module" src="/assets/static/js/App.js"></script>
  </body>
</html>
```

Your Flaxon deployment must expose the generated `dist/` files at `/assets/`. The Flaxon example in `examples/flaxon` includes a safe asset handler. In development, build first with `python build.py`, then run `flaxon run app:app --reload`.

## Passing server data

Pass small, non-sensitive initial values through Jinax:

```html
<script>window.__INITIAL__ = {{ initial_json | safe }};</script>
```

For user-controlled values, serialize with your framework's JSON helper rather than interpolating raw strings. Fetch private or changing data from an authenticated Python endpoint and enforce authorization on that endpoint.

