# Testing Teloce-Py

Run the normal regression suite from the repository root:

```bash
python -m pytest -q
```

Run the sustained compiler/build stress suite separately when changing the
parser, generator, CSS pipeline, imports, or build writer:

```bash
python -m pytest -q tests/stress
```

The stress suite compiles a large component with hundreds of bindings and CSS
rules, compiles it repeatedly to detect state leakage and nondeterminism,
feeds malformed sources through the diagnostic boundary, builds a 40-component
import graph, and checks generated JavaScript with Node's syntax checker.

For changes to browser behavior, also run the browser integration tests. They
require a local Chrome installation:

```bash
python -m pytest -q tests/integration/test_browser_e2e.py tests/integration/test_router_browser.py tests/integration/test_standalone_browser.py
```

Stress tests do not prove that application APIs, authentication, databases, or
deployment infrastructure are correct. Add application-level tests at the
framework boundary and run a production build before release:

```bash
teloce doctor --verbose
teloce lint --strict
teloce build --source-map --hash-assets --bundle
python -m build --sdist --wheel
python -m twine check dist/*
```

When a stress test fails, preserve the smallest failing `.vel` source and run
the direct compiler command to obtain structured diagnostics:

```bash
teloce compile path/to/App.vel -o /tmp/App.js --source-map
```

## Browser and deployment matrix

Run critical flows in a real supported browser, including initial mount, text
input, events, keyed list updates, route navigation, route refresh, lazy
imports, third-party DOM widgets, and teardown. Test both development/HMR and
the production output. A passing compiler test cannot detect a missing static
asset, a bad Vercel rewrite, or a browser-only API failure.
