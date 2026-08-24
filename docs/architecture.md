# Architecture

The pipeline is:

```text
.vel source -> SFC parser -> AST -> transforms -> JavaScript/CSS generator -> browser module
```

The Python framework serves the HTML shell and generated assets. The browser runtime provides signals, DOM updates, events, loops, conditions, components, and lifecycle behavior. Local component imports are resolved during the build.

## Build phases

1. **Discovery** finds `static/js`, templates, assets, configuration, and `.vel` files.
2. **SFC parsing** separates template, script, and style sections while preserving source locations for diagnostics.
3. **AST and transforms** interpret elements, interpolation, directives, loops, components, imports, and expressions.
4. **Generation** emits browser modules, runtime hooks, scoped CSS, and optional source maps.
5. **Asset handling** copies static assets, resolves local imports, optionally bundles modules, and can hash filenames.
6. **Serving** is performed by Flask, FastAPI, Django, Flaxon, a reverse proxy, or the Teloce development server.

## Runtime boundary

Python runs at build time and on the server. Generated JavaScript runs in the
browser. Browser events call Python APIs through HTTP or WebSockets; they do
not directly access Python objects or databases. This boundary is important for
security, testing, and deployment.

## Why the architecture is framework-agnostic

The compiler produces static browser assets and needs no knowledge of the
server's routing or ORM. Framework integration therefore consists of a build
step, a static-file route, and an HTML mount point. Authentication and
authorization remain server responsibilities.
