# Teloce ecosystem

Teloce is a component layer that sits between a Python application and the
browser. It does not replace the backend framework.

```text
Flask / FastAPI / Django / Flaxon / another Python server
                    ↓
             HTML shell + JSON APIs
                    ↓
       Teloce-Py compiled .vel assets
                    ↓
            browser runtime and DOM
```

## Teloce on npm

The npm Teloce project is the original JavaScript-oriented ecosystem for
`.vel` Single File Components. It provides the component language and browser
runtime for teams using a JavaScript or Node toolchain. The upstream project
also includes a VS Code extension package for authoring `.vel` files.

Useful upstream references:

- [Teloce repository](https://github.com/aldanedev-create/telonce)
- [Teloce VS Code extension](https://github.com/aldanedev-create/telonce/tree/main/packages/vscode-extension)

The npm ecosystem is useful when a team wants JavaScript package management,
Node-based plugins, or an existing npm build pipeline. Teloce-Py is useful when
the team wants to keep the application build and server workflow Python-first.

## What can be shared

Existing `.vel` source is the main portability boundary. Both implementations
are designed around:

- `<template>`, `<script>`, and `<style>` SFC sections;
- interpolation with `{{ expression }}`;
- reactive component data;
- events and event modifiers;
- conditional rendering;
- repeated lists and stable keys;
- components, props, slots, and lifecycle hooks;
- scoped component styles;
- filters, directives, plugins, and router concepts;
- a browser-side runtime that mounts into an HTML element.

Teloce-Py also accepts npm-style aliases such as `v-if`, `v-for`, `v-on`,
`v-bind`, `v-model`, `v-show`, `v-text`, and `v-html`, while preserving the
original Teloce forms such as `<if>`, `<for>`, `@click`, `:class`, `:show`, and
`:model`.

## What is not automatically portable

`.vel` source and browser behavior can often move with little or no change,
but Node-specific tooling cannot be assumed to work in Python:

| npm project item | Python project path |
|---|---|
| `.vel` component source | Compile with Teloce-Py and browser-test it |
| npm build plugin | Port it to a Python compiler plugin |
| Node-only package import | Replace with a browser-compatible module or Python API |
| npm dev server | Use `teloce dev`, `teloce watch`, or `python app.py` |
| npm deployment build | Use `teloce build` in CI |
| VS Code extension | Continue using the upstream extension; it is editor tooling |
| Python backend route | Keep it and expose the same HTTP/JSON contract |

Third-party plugins must be tested against the plugin API they use. A plugin
that transforms AST nodes can usually be redesigned in Python; a plugin that
depends on Node filesystem APIs, npm resolution, or a Node process needs a
deliberate port.

## Choosing the ecosystem

Choose npm Teloce when:

- the application already has a Node build pipeline;
- the team depends on JavaScript-only packages or plugins;
- frontend tooling is the primary development environment.

Choose Teloce-Py when:

- the backend is Flask, FastAPI, Django, Flaxon, or another Python server;
- the team wants `python app.py` to build and run the application;
- deployment is Python-only and Node is undesirable;
- `.vel` components should be compiled in Python CI.

Use both in a migration when necessary: keep the npm project running while
porting components and API contracts incrementally to the Python application.

## Migration workflow

1. Copy one representative `.vel` component into the Python project.
2. Compile it with `teloce build` or `build_project`.
3. Mount the generated module from the Python HTML shell.
4. Compare conditionals, keyed lists, forms, events, slots, styles, and router behavior in a browser.
5. Port only the npm plugins that the application actually uses.
6. Add the migrated component to CI and browser regression tests.
7. Repeat component by component.

The compatibility target is source and behavior compatibility, not an automatic
promise that every npm package can execute inside Python.
