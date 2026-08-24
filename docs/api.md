# Public API

## Compile one component

```python
from pathlib import Path
from teloce.compiler import compile_file

result = compile_file("static/js/App.vel")
if not result["success"]:
    raise RuntimeError(result["diagnostics"])
Path("static/js/App.js").write_text(result["code"], encoding="utf-8")
```

## Build a project

```python
from teloce.build import build_project
result = build_project(".", options={"source_maps": True, "dev": False})
```

The result contains build counters and generated files. The CLI is the recommended interface for application teams.

## Result shape

`compile_file` returns a dictionary containing `success`, generated `code`,
generated `css`, an optional source `map`, `diagnostics`, and parsed component
information. Always check `success` before writing output. `build_project`
returns build statistics and errors for a whole project.

## Server integration

The API is useful for custom build systems. Most applications should compile
before startup or in CI, write output to `dist/`, and configure the framework
to serve that directory. Do not compile arbitrary user-supplied `.vel` files
inside a public request without an explicit sandbox and resource policy.
