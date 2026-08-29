# Lesson 27: debug a production `.vel` application

Debug in layers and record the first failing boundary:

1. Run `teloce doctor --verbose`.
2. Run `teloce lint --strict` and compile the failing `.vel` file directly.
3. Open the debug dashboard locally and inspect its diagnostic location.
4. Check Network for the HTML shell, entry module, runtime, CSS, source map,
   and lazy chunks.
5. Check the browser console and preserve the generated module URL.
6. Call the Python API independently with the same request and payload.
7. Rebuild with a clean output directory and verify the manifest.
8. Reproduce the deployed failure with a production build, not HMR output.

For a blank page, first check the mount element and entry module. For text that
disappears while typing, check whether a broad rerender replaces the input. For
stale UI, inspect service-worker and browser caches. For router failures, test
both direct navigation and refresh. Never publish debug traces or credentials
while collecting a bug report.
