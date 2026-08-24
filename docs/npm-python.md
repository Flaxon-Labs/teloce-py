# npm Teloce and Python Teloce

Existing `.vel` files can be brought into a Python project. The Python compiler keeps original forms such as `@click`, `:class`, `<if>`, and `<for>`, while also accepting common `v-*` aliases.

Node-only plugins still need a port. Compile representative components and test them in a browser before migrating a large application.

## Runtime comparison

The npm workflow normally uses JavaScript package tooling to produce browser
assets. The Python workflow uses the same `.vel` idea but compiles through
Teloce-Py and serves the result from a Python framework. In both cases, the
browser needs JavaScript; “Python-native” describes the compiler and server
workflow, not a browser that executes Python.

Keep the HTTP contract stable during migration. A component can move first,
then its API route can be moved from an npm server to Flask, FastAPI, Django,
or Flaxon independently.
