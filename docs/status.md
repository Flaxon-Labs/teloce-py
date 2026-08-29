# Teloce-Py status and compatibility

Teloce-Py is currently a beta release. The compiler, runtime, CLI, CSS
pipeline, router, SSR adapter, and browser regression suite are usable, but
the project is not a drop-in replacement for a full JavaScript or TypeScript
toolchain.

## Feature status

| Area | Status | Notes |
| --- | --- | --- |
| `.vel` templates and SFC parsing | Supported | Compile and test in CI. |
| Original Teloce directives | Supported | `if`, `for`, `@click`, `@class`, and related forms remain available. |
| `v-*` aliases | Supported | Use aliases where they fit your project. |
| Component imports and scoped CSS | Supported | Local imports are discovered during project builds. |
| Signals and generated reactivity | Supported | Test browser behavior for application-specific state. |
| Keyed DOM updates | Supported | Keys must be stable and unique among siblings. |
| Router and lifecycle cleanup | Supported | Router is client navigation, not authorization. |
| HMR | Development feature | Never expose the HMR endpoint in production. |
| SSR/static output | Supported with Jinax/Jinja-compatible engines | Browser events still hydrate on the client. |
| Built-in JavaScript parser | Supported analysis surface | Not a complete ECMAScript or TypeScript compiler. |
| Symbol-level bundling/tree-shaking | Optional | Use esbuild for industrial JavaScript bundling. |
| TypeScript | Limited compatibility pass | Common annotations are stripped; use TypeScript/SWC for full syntax and type-checking. |

## Release gate

Before publishing a release, run `teloce doctor --verbose`, strict linting,
the complete tests, a production build, `python -m build`, and `twine check`.
The exact supported Python and browser versions should be recorded in the
release notes for each release.
