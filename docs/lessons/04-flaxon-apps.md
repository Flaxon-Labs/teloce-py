# Lesson 4: build a Flaxon application with Python

Flaxon provides the Python application layer. Teloce-Py compiles the `.vel` UI layer. A typical request flows like this:

```text
browser -> Flaxon route -> Python service/database -> JSON response -> .vel state -> rendered UI
```

## Minimal Flaxon entry point

```python
from flaxon import Flaxon

app = Flaxon()

@app.get("/api/health")
async def health():
    return {"ok": True, "service": "demo"}
```

Serve the compiled assets from your configured public directory and mount the generated component in the page. Keep secrets, database queries, authorization, and validation on the server.

## Frontend API call from `.vel`

```html
<script>
export default {
  data() { return { status: "Loading..." }; },
  async mounted() {
    const response = await fetch("/api/health");
    const data = await response.json();
    this.status = data.ok ? "Ready" : "Unavailable";
  }
};
</script>
```

The same generated component can be served by Flask, FastAPI, Django, or Flaxon. The framework only needs to serve the HTML and generated JavaScript and expose the API routes used by the component.

## Production habits

- Validate all API input in Python.
- Return predictable JSON shapes.
- Handle loading, empty, error, and retry states in `.vel`.
- Use CSRF protection where cookie-authenticated mutations exist.
- Add rate limits to expensive endpoints.
- Never trust browser-only security checks.
- Build assets in CI and deploy the generated output.

## Good project ideas

- Flask chat application with streamed messages
- FastAPI CMS with an editor and media library
- Django web scanner dashboard with permission checks
- Flaxon network monitor with local-first IndexedDB history
- Student workspace with notes, recordings, and file export

The `.vel` layer accelerates the interface; Python remains the source of truth for application behavior.
