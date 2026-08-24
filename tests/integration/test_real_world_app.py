"""End-to-end smoke test for a realistic interactive Teloce component."""

import subprocess
import tempfile
from pathlib import Path
from teloce.compiler.compiler import Compiler
from teloce.router.compiler import RouterCompiler
from teloce.router.generator import RouterGenerator


def test_real_world_todo_component_and_router():
    source = '''
<template>
  <main class="app">
    <h1>{{ title }}</h1>
    <button @click="increment">{{ count }}</button>
    <if condition="show">
      <ul><for item in items><li>{{ item }}</li></for></ul>
    </if>
  </main>
</template>
<script>
export default {
  data() { return { title: "Todo", count: 0, show: true, items: ["one", "two"] }; },
  methods: { increment() { this.count++; } }
}
</script>
<style scoped>.app { color: red; }</style>
'''
    result = Compiler().compile(source, "Todo.vel")
    assert result["success"], result["diagnostics"]
    assert "mount(target" in result["code"]
    assert "Todo" in result["code"]
    assert result["css"] and "data-v-" in result["css"]
    with tempfile.TemporaryDirectory() as directory:
        generated = Path(directory) / "Todo.js"
        generated.write_text(result["code"], encoding="utf-8")
        checked = subprocess.run(["node", "--check", str(generated)], capture_output=True, text=True)
        assert checked.returncode == 0, checked.stderr + "\n" + result["code"]

    router = RouterCompiler().compile({
        "mode": "history",
        "base": "/app",
        "routes": [
            {"path": "/", "component": "HomePage", "name": "home"},
            {"path": "/todos", "component": "TodoPage", "props": True},
        ],
    })
    assert router is not None
    router_js = RouterGenerator().generate(router)
    assert "createRouter" in router_js
    assert 'mode: "history"' in router_js
