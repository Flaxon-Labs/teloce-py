# Fast Dev-Facts: speed up Teloce development

## The fastest reliable loop

```text
edit .vel -> teloce lint -> run Python app -> test in browser -> commit source
```

Use this short loop while designing. Run the full production build and browser
regression suite before a release.

## High-value habits

1. Start with `teloce create`; it generates a working shell and config.
2. Run `teloce lint --fix` after moving markup or changing directives.
3. Use `python app.py` when the app's Python entry point already builds assets.
4. Use `teloce dev` for the compiler server and HMR during component work.
5. Give every repeated item a stable `:key`; never use a random value.
6. Keep form inputs stable during updates; do not replace their parent on every
   keystroke.
7. Put third-party editors, canvases, and media players behind lifecycle hooks
   and dispose them on unmount.
8. Lazy-load large pages and libraries such as Three.js.
9. Check Network before changing code: a 404 runtime or CSS file is not a
   reactivity bug.
10. Keep API response shapes explicit and test them independently of the UI.

## Daily commands

```bash
teloce doctor --verbose
teloce lint --strict
python -m pytest -q
teloce build --source-map --hash-assets --report
```

For one component:

```bash
teloce compile src/components/App.vel -o dist/App.js --source-map
```

## Performance facts

- Shared runtime extraction prevents every component from embedding duplicate
  helpers.
- Teloce component/filter selection removes unused framework-level pieces.
- Optional esbuild is needed for whole-program JavaScript tree-shaking,
  splitting, minification, and final bundle analysis.
- Hashed assets make browser caching safe after deployment.
- Static or SSR output is faster for content that does not need browser state.
- IndexedDB is fast local storage, not a shared team database.

## Debug facts

- Blank screen: check `#app`, entry module status, runtime status, and console.
- Text not visible while typing: inspect input replacement and broad rerenders.
- Router works locally but not after refresh: configure the server shell
  fallback or use hash routing.
- HMR is not production behavior; reproduce release bugs with `teloce build`.
- A successful compile does not prove that an API, database, or authorization
  rule works.

## Commit only what matters

Commit `.vel` source, Python code, configuration, tests, lock files, and
deployment configuration. Do not commit secrets, `.env`, `__pycache__`, local
IndexedDB data, or generated output unless your hosting workflow explicitly
requires it. See [project structure](file-structure.md), [testing](../testing.md),
and [troubleshooting](../troubleshooting.md) when the short loop stops being
clear.
