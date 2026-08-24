# Compiler

The compiler reads the `<template>`, `<script>`, and `<style>` sections of a `.vel` file. It validates structure, transforms bindings and directives, generates a self-contained browser module, and emits CSS and optional source maps.

Compilation should happen during development or CI. The production server should serve the generated files rather than compiling on every request.

## Inputs and outputs

The compiler accepts a `.vel` source file or a project directory. A component
can contain a template, JavaScript component definition, and CSS. The output
normally includes a JavaScript module and may include CSS, source maps, hashed
asset names, and a dependency-aware bundle.

```python
from teloce.compiler import compile_file

result = compile_file("static/js/App.vel")
if result["success"]:
    print(result["code"])
else:
    print(result["diagnostics"])
```

For applications use `build_project` or `teloce build`, because project builds
also discover local imports and copy assets.

## Build modes

- Development mode favors readable output, source maps, watching, and HMR.
- Production mode favors deterministic output, optional minification, hashed
  assets, bundles, and clean output directories.

Compiler success does not replace browser testing. A component can be valid
syntax and still have an incorrect API response, authorization assumption, or
browser interaction.
