# JavaScript, TypeScript, and production bundling

Teloce's default JavaScript boundary parser is written from scratch in
`src/teloce/javascript/parser.py`. It is dependency-free and source
preserving. It tokenizes literals/comments, validates balanced syntax, and
understands the top-level import/export boundaries needed by `.vel` files.
It does not claim to be a complete ECMAScript or TypeScript compiler. Teloce
has a limited compatibility pass for common TypeScript annotations; that pass
is not type-checking.

For dependency-free editor and diagnostic tooling, the package also exposes a
source-preserving language AST:

```python
from teloce.javascript import parse_javascript_language


program = parse_javascript_language(
    "const total = prices.reduce((a, b) => a + b, 0);"
)
declaration = program.body[0]
assert declaration.kind == "VariableDeclaration"
assert declaration.children[0].kind == "VariableDeclarator"
```

The language parser reports balanced-syntax errors with line and column
locations, optional repair suggestions, and preserves the original source of
every node. Its recursive AST covers common declarations and statements,
blocks, conditionals, loops, functions, classes, module boundaries, arrows,
calls, members, `new`, arrays/objects, spread/rest, unary/binary/assignment,
conditional, optional-chaining, and update expressions. It does not promise
support for every current or future ECMAScript proposal.

That distinction matters: Teloce can safely compile its template language
without forcing a Node toolchain, but full JavaScript language parsing,
TypeScript type erasure, symbol linking, and industrial dead-code elimination
are separate compiler jobs.

## What the optional packages do

| Tool | What it provides | Where it fits |
| --- | --- | --- |
| TypeScript compiler API (`typescript`) | Microsoft's parser, binder, type checker, emitter, source maps, and language-service data | Full TypeScript/JavaScript analysis and transpilation; normally run in a Node build step |
| Tree-sitter with JavaScript/TypeScript grammars | Fast incremental concrete syntax trees and error nodes | Editor tooling, syntax-aware transforms, and reliable analysis; it is not a type checker or bundler |
| SWC (`@swc/core`) | Rust-based JavaScript/TypeScript/JSX parser and transformer | Fast transpilation and syntax lowering in a Node build pipeline |
| esbuild | Bundling, ESM-aware tree-shaking, code splitting, minification, and source maps | Production asset optimization after Teloce emits JavaScript |

The TypeScript compiler API models a pipeline of parser, binder, checker,
emitter, and services. Tree-sitter provides syntax trees and incremental
editing, but does not replace semantic type checking. SWC is a transformer,
while esbuild is the most direct fit for final bundling and tree-shaking.

References: [TypeScript Compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API),
[Tree-sitter TypeScript grammars](https://github.com/tree-sitter/tree-sitter-typescript),
[SWC parser configuration](https://swc.rs/docs/usage/core), and
[esbuild tree-shaking and code splitting](https://github.com/evanw/esbuild/blob/main/docs/architecture.md).

## TypeScript in a `.vel` file today

```html
<script lang="ts">
interface User { id: number; name: string; }
const user: User = { id: 1, name: 'Ada' };
</script>
```

For `lang="ts"`, Teloce removes a limited set of type-only declarations,
common parameter/return/variable annotations, type imports, assertions, and
simple enums before generating browser JavaScript. It does not type-check the
program, resolve types, support every TypeScript construct, or provide
TypeScript language-service diagnostics. Complex generics, decorators, JSX,
advanced enum behavior, declaration merging, and many newer TS features should
be compiled by TypeScript or SWC first.

## How esbuild fits

When you run:

```bash
teloce build --bundle --bundler esbuild --minify --hash-assets --source-map
```

the flow is:

```text
.vel (lang="ts")
  -> Teloce removes supported type-only syntax
  -> Teloce generates JavaScript modules and CSS
  -> esbuild bundles generated modules
  -> esbuild tree-shakes, splits, minifies, and writes source maps
  -> browser loads the final assets
```

esbuild does not make Teloce's parser a TypeScript type checker. If the
generated module imports a `.ts` file, esbuild can transpile that file only if
the project has configured esbuild as the bundling entry and the syntax is
within esbuild's supported transform surface. Teloce itself still discovers
and compiles `.vel` files first.

## Why Teloce currently stays dependency-free

The from-scratch parser keeps `pip install teloce-py` small and lets Flask,
Django, FastAPI, and Flaxon projects compile `.vel` components without a
Node dependency. It is appropriate for Teloce's SFC boundary and diagnostics.
The compiler must not silently use regexes to decide module boundaries. The
parser test suite includes semicolon-free modules, nested delimiter failures,
modern numeric/regex/template literals, arrow functions, spread/rest, and
postfix updates.

For applications containing arbitrary modern JavaScript or TypeScript, use a
separate optional build stage. Keep Teloce responsible for `.vel` templates,
component metadata, CSS, and runtime generation; give emitted `.js` files to
esbuild or another approved JavaScript tool. This avoids pretending that a
small embedded parser can safely rewrite every ECMAScript proposal.

## Recommended full TypeScript arrangement

For applications that need full TypeScript, use a separate Node build stage:

1. Parse and transpile the `<script lang="ts">` block with TypeScript or SWC.
2. Return source-mapped JavaScript to Teloce's generator.
3. Run the emitted modules through esbuild for tree-shaking, splitting,
   hashing, minification, and browser-target selection.
4. Preserve Teloce diagnostics and map them back to the `.vel` source.

Do not add a TypeScript package just to make a simple `.vel` component work.
The current supported path is plain JavaScript plus Teloce's dependency-free
parser.

## Current Teloce commands

```powershell
# Development compiler/runtime path
python app.py

# Production output with Teloce's built-in optimizer
teloce build --hash-assets --report --max-size 250000

# Add Jinax server-rendered artifacts
teloce build --static

# Emit lazy local component imports
teloce build --lazy-components SettingsPanel
```

Teloce's built-in optimizer performs AST-aware local component import
tree-shaking, built-in filter selection, lazy import emission, shared runtime
extraction, keyed DOM reconciliation, and size reporting. It is not a
replacement for a full JavaScript bundler's symbol-level dead-code analysis;
use an optional bundler when the application needs that guarantee.

## Expression security

Generated components and the standalone runtime interpret template expressions
with Teloce's constrained evaluator. They do not use `eval()` or `Function()`
and reject dangerous property paths such as `constructor`, `prototype`, and
`__proto__`. Unsupported expressions resolve safely and can be diagnosed in
development. Do not treat browser expressions as a security boundary: keep
authorization, validation, secrets, and database work in Python.

Older applications may still pass an `unsafe_eval` setting. It is retained as
a compatibility-shaped configuration value but does not enable dynamic code
execution in current generated or standalone runtimes.

## Jinax and Python frameworks

`render_ssr()` accepts a Jinax/Jinja-compatible engine. Flaxon can provide
Jinax directly, while Flask, Django, and FastAPI applications can pass their
framework-owned Jinja environment or template adapter. The SSR translator
only evaluates server-safe template directives; browser event handlers and
unsafe JavaScript are not executed on the server.
