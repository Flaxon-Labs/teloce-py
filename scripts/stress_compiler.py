"""Exercise the editable Teloce compiler with broad, repeatable inputs.

Run from the repository root:

    python scripts/stress_compiler.py

This is a compiler/build stress runner. Browser interaction tests remain in
``tests/integration/test_browser_e2e.py`` and require a working browser.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from teloce.build.builder import Builder
from teloce.compiler.compiler import Compiler


def component(index: int, *, malformed: bool = False) -> str:
    if malformed:
        return "<template><main><div>unterminated"
    cards = "".join(
        f'<li v-for="item in items" :key="item.id">{{{{ item.name }}}}</li>'
        for _ in range(3)
    )
    return f"""<template>
  <main class="screen-{index}">
    <h1>{{ title }}</h1>
    <input v-model="query" @input="filterItems" />
    <button v-on:click="increment">{{ count }}</button>
    <p v-if="visible">{{ query | uppercase }}</p>
    <ul>{cards}</ul>
  </main>
</template>
<script>
export default {{
  data() {{ return {{ title: "Stress {index}", query: "", count: 0,
    visible: true, items: [{{ id: 1, name: "One" }}, {{ id: 2, name: "Two" }}] }}; }},
  computed: {{ total() {{ return this.items.length; }} }},
  methods: {{ increment() {{ this.count++; }}, filterItems() {{ this.visible = true; }} }}
}};
</script>
<style scoped>
.screen-{index} {{ display: grid; gap: .5rem; }}
@media (max-width: 40rem) {{ .screen-{index} {{ display: block; }} }}
</style>"""


def node_check(path: Path) -> None:
    result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"node --check failed for {path}: {result.stderr}")


def main() -> int:
    compiler = Compiler({"dev": True, "source_maps": True})
    passed = 0
    outputs: list[tuple[int, str]] = []
    for index in range(100):
        result = compiler.compile(component(index), f"Stress{index}.vel")
        if not result["success"]:
            raise RuntimeError(f"valid case {index} failed: {result['diagnostics']}")
        outputs.append((index, result["code"]))
        passed += 1

    # Compile every case, but avoid spawning 100 independent V8 processes on
    # Windows. Check representative outputs across the run instead; the
    # compiler's output is deterministic and the full source is still tested
    # above for successful generation.
    with tempfile.TemporaryDirectory(prefix="teloce-stress-") as directory:
        for index, code in (outputs[0], outputs[49], outputs[-1]):
            output = Path(directory) / f"Stress{index}.js"
            output.write_text(code, encoding="utf-8")
            node_check(output)

    for index in range(20):
        result = compiler.compile(component(index, malformed=True), f"Broken{index}.vel")
        if result["success"] or not result["diagnostics"]["errors"]:
            raise RuntimeError(f"malformed case {index} did not produce diagnostics")
        passed += 1

    with tempfile.TemporaryDirectory(prefix="teloce-build-stress-") as directory:
        root = Path(directory)
        js = root / "static" / "js" / "components"
        js.mkdir(parents=True)
        imports = []
        names = []
        for index in range(25):
            name = f"Card{index}"
            (js / f"{name}.vel").write_text(
                f"<template><article>{index}</article></template>", encoding="utf-8"
            )
            imports.append(f'import {name} from "./components/{name}.vel";')
            names.append(name)
        (root / "static" / "js" / "App.vel").write_text(
            "\n".join(imports)
            + f'\n<template><main>{"".join(f"<{name} />" for name in names)}</main></template>\n'
            + f'<script>export default {{ components: {{ {", ".join(names)} }} }};</script>',
            encoding="utf-8",
        )
        result = Builder({"dev": True, "clean": True, "source_maps": True}).build(root)
        if result["failed"] or result["compiled"] != 26:
            raise RuntimeError(f"import graph failed: {result}")
        node_check(root / "dist" / "static" / "js" / "App.js")

    print(f"Teloce compiler stress passed: {passed} component cases + 26-file import graph")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
