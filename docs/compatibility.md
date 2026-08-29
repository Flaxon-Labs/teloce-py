# npm Teloce and Teloce-Py compatibility

Teloce-Py keeps the original `.vel` authoring style where practical while
adding Python-native build and framework integration.

| Original style | Teloce-Py equivalent | Status |
| --- | --- | --- |
| `@click="save()"` | `@click="save()"` | Compatible |
| `@class="active: selected"` | `@class="active: selected"` | Compatible |
| `<if condition="open">` | `<if condition="open">` | Compatible |
| `<for item="row" in="rows">` | `<for item="row" in="rows">` | Compatible |
| `v-if="open"` | `v-if="open"` | Alias supported |
| `v-for="row in rows" :key="row.id"` | Same syntax | Supported; use stable keys |
| npm bundler plugins | Teloce plugins or optional esbuild | Requires migration |
| Node-only runtime imports | Generated Teloce runtime assets | Replace import path |
| TypeScript build pipeline | Separate Node/TS step | Teloce only strips limited common TS syntax; no type-checker |

The Python package does not promise that every npm plugin, proposal-specific
JavaScript transform, or TypeScript type feature will compile unchanged. Move
those transformations to TypeScript/SWC/esbuild and give the resulting
JavaScript to the Teloce build, or rewrite the behavior as a Teloce plugin.

Migration order: compile one component, verify generated assets, test events
and keyed lists in a browser, then migrate router, plugins, CSS, and deployment
configuration one boundary at a time.
