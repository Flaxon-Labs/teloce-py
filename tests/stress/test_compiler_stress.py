"""Stress and regression coverage for large, repetitive real-world components."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from teloce.build.builder import Builder
from teloce.compiler.compiler import Compiler


def _large_component() -> str:
    cards = "\n".join(
        f'      <li class="card card-{index}"><span>{{{{ item-{index} }}}}</span></li>'
        for index in range(180)
    )
    styles = "\n".join(
        f".card-{index} {{ padding: {index % 8 + 1}px; color: rgb({index % 255}, 80, 140); }}"
        for index in range(180)
    )
    data = ", ".join(f'"item-{index}": "Value {index}"' for index in range(180))
    return f'''<template>
  <main class="large-app">
    <header><h1>{{{{ title }}}}</h1><button @click="increment">{{{{ count }}}}</button></header>
    <if condition="visible">
      <ul><for item in items key="item.id"><li>{{{{ item.name }}}}</li></for></ul>
    </if>
    <section class="cards">{cards}
    </section>
  </main>
</template>
<script>
export default {{
  data() {{ return {{ title: "Stress", count: 0, visible: true, items: [] , {data} }}; }},
  methods: {{ increment() {{ this.count++; }} }}
}};
</script>
<style scoped>
.large-app {{ display: grid; gap: 1rem; }}
{styles}
</style>'''


def _node_check(path: Path) -> None:
    checked = subprocess.run(
        ["node", "--check", str(path)], capture_output=True, text=True
    )
    assert checked.returncode == 0, checked.stderr


def test_large_component_compiles_to_valid_javascript_and_css():
    result = Compiler({"source_maps": True}).compile(_large_component(), "Stress.vel")
    assert result["success"], result["diagnostics"]
    assert len(result["code"]) > 20_000
    assert result["css"].count("data-v-") >= 180

    pytest.importorskip("tempfile")
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "Stress.js"
        output.write_text(result["code"], encoding="utf-8")
        _node_check(output)
        assert result["map"]["version"] == 3


def test_repeated_compilation_is_stable_and_does_not_accumulate_diagnostics():
    source = _large_component()
    compiler = Compiler({"source_maps": False})
    outputs = []
    for _ in range(12):
        result = compiler.compile(source, "Repeated.vel")
        assert result["success"], result["diagnostics"]
        outputs.append(result["code"])
    assert len(set(outputs)) == 1


@pytest.mark.parametrize(
    "source",
    [
        "",
        "<template>",
        "<script>export default {",
        "<template><div></template>",
        "<template><for item in items><span>{{ item }}</span></for>",
        "<template><div>",
    ],
)
def test_malformed_sources_return_diagnostics_without_crashing(source: str):
    result = Compiler().compile(source, "Malformed.vel")
    assert result["success"] is False
    assert result["diagnostics"]["errors"]
    assert all("message" in error for error in result["diagnostics"]["errors"])


def test_large_import_graph_builds_without_output_recursion(tmp_path: Path):
    root = tmp_path / "project"
    js = root / "static" / "js"
    components = js / "components"
    components.mkdir(parents=True)
    imports = []
    registrations = []
    for index in range(40):
        name = f"Card{index}"
        (components / f"{name}.vel").write_text(
            f'<template><article class="card">Card {index}</article></template>',
            encoding="utf-8",
        )
        imports.append(f'import {name} from "./components/{name}.vel";')
        registrations.append(f"{name}")
    tags = "".join(f"<{name} />" for name in registrations)
    (js / "App.vel").write_text(
        "\n".join(imports)
        + f'\n<template><main>{tags}</main></template>\n'
        + f'<script>export default {{ components: {{ {", ".join(registrations)} }} }};</script>',
        encoding="utf-8",
    )

    result = Builder({"source_maps": False}).build(root)
    assert result["failed"] == 0, result["errors"]
    assert result["compiled"] == 41
    assert not (root / "dist" / "public").exists()
    _node_check(root / "dist" / "static" / "js" / "App.js")
