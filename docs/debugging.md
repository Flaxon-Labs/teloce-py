# Debugging `.vel` applications

Teloce applications have several layers. Debug the layer that owns the failure:

```text
.vel source -> compiler -> generated JavaScript/CSS -> browser runtime -> Python API -> database/deployment
```

## Start with the compiler

```bash
teloce doctor --verbose
teloce lint --strict
teloce build --out-dir dist --source-map
```

Fix the first diagnostic before changing later files. Confirm that the entry component and every imported `.vel` file appear in the build summary.

For an isolated component:

```python
from teloce.compiler import compile_file

result = compile_file("static/js/App.vel")
if not result["success"]:
    for diagnostic in result["diagnostics"]:
        print(diagnostic)
```

## Use the debug dashboard

```bash
teloce debug
teloce debug --port 9000 --host 127.0.0.1 --no-open
```

Open `http://127.0.0.1:9000`. The local dashboard shows the project root, Python and Teloce versions, discovered `.vel` paths, compile diagnostics, pass/error/warning totals, and a Refresh action.

Its JSON endpoints are useful in scripts and CI:

```bash
curl http://127.0.0.1:9000/api/health
curl http://127.0.0.1:9000/api/project
curl http://127.0.0.1:9000/api/diagnostics
```

The dashboard is a diagnostics inspector. It does not inspect live component state, browser storage, server logs, or production traffic. Keep it bound to localhost.

## Check the browser boundary

Use DevTools Console, Network, and Application tabs. Verify generated `.js` and `.css` files return `200`, inspect API response JSON, and check service workers, Cache Storage, and IndexedDB.

Test a user flow, not only page load:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://127.0.0.1:5000")
    field = page.locator("input[aria-label='Search']")
    field.fill("python")
    assert field.input_value() == "python"
    page.locator("form.search-form button[type=submit]").click()
    browser.close()
```

If typing clears, a parent `@input` handler is probably changing reactive state on every keystroke. Use `v-model` locally and a separate custom event with `@input.stop` for suggestions.

## Check API and Python separately

```bash
curl http://127.0.0.1:5000/api/health
curl "http://127.0.0.1:5000/api/search?q=python"
```

If the API is correct but the UI is empty, compare the response shape with the expressions in the `.vel` template. An API returning `{ "results": [...] }` must be assigned with `this.results = data.results`.

## Check deployment

```bash
vercel logs <deployment-url>
vercel env ls
```

Common production failures are Python metadata allowing 3.10 while a dependency requires 3.11+, missing `Jinja2` for template rendering, setuptools discovering `public/` as a Python package, an absent Neon schema, or a service worker serving an old bundle.

After a browser-runtime fix, increment the service-worker cache name, redeploy, and hard-refresh. Never put database URLs or cron secrets in `.vel`, JavaScript, screenshots, or Git.

## Checklist

- [ ] `teloce doctor --verbose` passes.
- [ ] `teloce lint --strict` passes.
- [ ] Every `.vel` import resolves.
- [ ] `teloce build` reports zero failed files.
- [ ] Generated assets return `200`.
- [ ] API endpoints work without the UI.
- [ ] Browser typing, clicks, loops, and empty states are tested.
- [ ] IndexedDB and service-worker caches are checked.
- [ ] Deployment logs and environment variables are checked.
- [ ] The fix is retested in a fresh browser context.
