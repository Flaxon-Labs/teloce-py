"""Real browser smoke test for generated component behavior."""

import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

from teloce.build import build_project
from teloce.cli.server import start_dev_server


def _chrome() -> str | None:
    candidates = [
        shutil.which("chrome"),
        shutil.which("chromium"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ]
    return next((candidate for candidate in candidates if candidate and Path(candidate).exists()), None)


def _dump_dom(url: str, budget: int):
    """Run Chrome with disposable profiles and retry transient startup stalls."""
    failure = None
    for _attempt in range(2):
        with tempfile.TemporaryDirectory(prefix="teloce-chrome-") as profile:
            try:
                return subprocess.run(
                    [_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu",
                     "--disable-software-rasterizer", "--disable-extensions", "--disable-sync",
                     "--disable-background-networking", "--disable-component-update",
                     "--no-first-run", "--no-default-browser-check",
                     f"--user-data-dir={profile}", "--dump-dom",
                     f"--virtual-time-budget={budget}", url],
                    capture_output=True, text=True, timeout=30,
                )
            except subprocess.TimeoutExpired as error:
                failure = error
    raise failure


@pytest.mark.skipif(_chrome() is None, reason="Chrome/Chromium is not installed")
def test_generated_component_renders_and_reacts_in_real_chrome(tmp_path: Path):
    (tmp_path / "static" / "js").mkdir(parents=True)
    (tmp_path / "static" / "js" / "App.vel").write_text(
        '<template><button @click="increment">{{ count }}</button></template>'
        '<script>export default { data() { return { count: 0 }; }, methods: { increment() { this.count++; } } };</script>',
        encoding="utf-8",
    )
    build_project(tmp_path, options={"dev": True, "source_maps": False})
    (tmp_path / "dist" / "index.html").write_text(
        '<div id="app"></div><script type="module">'
        'import { mount } from "/static/js/App.js"; mount("#app"); '
        'setTimeout(() => { document.querySelector("button").click(); '
        'setTimeout(() => document.title = document.querySelector("button").textContent, 50); }, 50);'
        '</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path / "dist")
    try:
        time.sleep(0.1)
        result = _dump_dom(f"http://127.0.0.1:{server.server_port}/?no_hmr=1", 1000)
        assert result.returncode == 0, result.stderr
        assert "<title>1</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome/Chromium is not installed")
def test_generated_component_hydrates_existing_server_rendered_markup(tmp_path: Path):
    (tmp_path / "static" / "js").mkdir(parents=True)
    (tmp_path / "static" / "js" / "App.vel").write_text(
        '<template><button @click="increment">{{ count }}</button></template>'
        '<script>export default { data() { return { count: 0 }; }, methods: { increment() { this.count++; } } };</script>',
        encoding="utf-8",
    )
    build_project(tmp_path, options={"dev": True, "source_maps": False})
    (tmp_path / "dist" / "index.html").write_text(
        '<div id="app"><button data-server="yes">0</button></div>'
        '<script type="module">import { mount } from "/static/js/App.js"; '
        'mount("#app"); setTimeout(() => { const button = document.querySelector("button"); '
        'document.title = (button.dataset.server || "missing") + ":" + button.textContent; }, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path / "dist")
    try:
        time.sleep(0.1)
        result = _dump_dom(f"http://127.0.0.1:{server.server_port}/?no_hmr=1", 1000)
        assert result.returncode == 0, result.stderr
        # The existing node is reused, and its server-only attribute is
        # removed because it is absent from the client template.
        assert "<title>missing:0</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome/Chromium is not installed")
def test_keyed_loop_preserves_dom_nodes_when_items_reorder(tmp_path: Path):
    (tmp_path / "static" / "js").mkdir(parents=True)
    (tmp_path / "static" / "js" / "App.vel").write_text(
        '<template><button @click="swap">Swap</button><ul><for key="id" item="item" in="items"><li>{{ item.id }}:{{ item.name }}</li></for></ul></template>'
        '<script>export default { data() { return { items: [{id: 1, name: "A"}, {id: 2, name: "B"}] }; }, methods: { swap() { this.items = [this.items[1], this.items[0]]; } } };</script>',
        encoding="utf-8",
    )
    build_project(tmp_path, options={"dev": True, "source_maps": False})
    (tmp_path / "dist" / "index.html").write_text(
        '<div id="app"></div><script type="module">import { mount } from "/static/js/App.js"; mount("#app"); '
        'setTimeout(() => { const first = document.querySelector("li"); first.dataset.keep = "yes"; '
        'document.querySelector("button").click(); setTimeout(() => document.title = document.querySelectorAll("li")[1].dataset.keep + ":" + document.querySelectorAll("li")[1].textContent, 50); }, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path / "dist")
    try:
        time.sleep(0.1)
        result = _dump_dom(f"http://127.0.0.1:{server.server_port}/?no_hmr=1", 1200)
        assert result.returncode == 0, result.stderr
        assert "<title>yes:1:A</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome/Chromium is not installed")
def test_nested_loops_render_in_real_chrome(tmp_path: Path):
    (tmp_path / "static" / "js").mkdir(parents=True)
    (tmp_path / "static" / "js" / "App.vel").write_text(
        '<template><ul><for item="group" in="groups"><for item="item" in="group.items"><li>{{ group.name }}:{{ item }}</li></for></for></ul></template>'
        '<script>export default { data() { return { groups: [{name: "A", items: [1, 2]}] }; } };</script>',
        encoding="utf-8",
    )
    build_project(tmp_path, options={"dev": True, "source_maps": False})
    (tmp_path / "dist" / "index.html").write_text(
        '<div id="app"></div><script type="module">import { mount } from "/static/js/App.js"; mount("#app"); '
        'setTimeout(() => document.title = document.querySelector("ul").textContent, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path / "dist")
    try:
        time.sleep(0.1)
        result = _dump_dom(f"http://127.0.0.1:{server.server_port}/?no_hmr=1", 1000)
        assert result.returncode == 0, result.stderr
        assert "A:1A:2" in result.stdout
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome/Chromium is not installed")
def test_keyed_reconciliation_preserves_dom_identity_when_reordered(tmp_path: Path):
    (tmp_path / "static" / "js").mkdir(parents=True)
    (tmp_path / "static" / "js" / "App.vel").write_text(
        '<template><ul><li v-for="item in items" v-bind:key="item.id">{{ item.name }}</li></ul></template>'
        '<script>export default { data() { return { items: [{id: "a", name: "A"}, {id: "b", name: "B"}] }; } };</script>',
        encoding="utf-8",
    )
    build_project(tmp_path, options={"dev": True, "source_maps": False})
    (tmp_path / "dist" / "index.html").write_text(
        '<div id="app"></div><script type="module">import { mount } from "/static/js/App.js"; const app = mount("#app"); '
        'setTimeout(() => { document.querySelectorAll("li")[1].dataset.keep = "yes"; app.state.items = [app.state.items[1], app.state.items[0]]; '
        'setTimeout(() => document.title = document.querySelectorAll("li")[0].dataset.keep + ":" + document.querySelector("ul").textContent, 50); }, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path / "dist")
    try:
        time.sleep(0.1)
        result = _dump_dom(f"http://127.0.0.1:{server.server_port}/?no_hmr=1", 1500)
        assert result.returncode == 0, result.stderr
        assert "<title>yes:BA</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome/Chromium is not installed")
def test_css_module_dynamic_class_binding_works_in_real_chrome(tmp_path: Path):
    (tmp_path / "static" / "js").mkdir(parents=True)
    (tmp_path / "static" / "js" / "App.vel").write_text(
        '<template><div :class="classes">Ready</div></template>'
        '<script>export default { data() { return { classes: { card: true } }; } };</script>'
        '<style module>.card { color: red; }</style>',
        encoding="utf-8",
    )
    build_project(tmp_path, options={"dev": True, "source_maps": False})
    (tmp_path / "dist" / "index.html").write_text(
        '<div id="app"></div><script type="module">import { mount } from "/static/js/App.js"; mount("#app"); '
        'setTimeout(() => document.title = document.querySelector("#app > div").className, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path / "dist")
    try:
        time.sleep(0.1)
        result = _dump_dom(f"http://127.0.0.1:{server.server_port}/?no_hmr=1", 1000)
        assert result.returncode == 0, result.stderr
        assert "<title>card__App_" in result.stdout
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome/Chromium is not installed")
def test_component_hmr_preserves_state_in_real_chrome(tmp_path: Path):
    (tmp_path / "static" / "js").mkdir(parents=True)
    (tmp_path / "static" / "js" / "App.vel").write_text(
        '<template><button>{{ count }}</button></template>'
        '<script>export default { data() { return { count: 0 }; } };</script>',
        encoding="utf-8",
    )
    build_project(tmp_path, options={"dev": True, "source_maps": False})
    (tmp_path / "dist" / "index.html").write_text(
        '<div id="app"></div><script type="module">import { mount } from "/static/js/App.js"; mount("#app"); '
        'setTimeout(async () => { const record = [...window.__teloce_hmr_instances.values()][0].values().next().value; '
        'record.state.count = 7; await window.__teloce_hmr_reload(); '
        'setTimeout(() => document.title = document.querySelector("button").textContent, 50); }, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path / "dist", hmr=False)
    try:
        time.sleep(0.1)
        result = _dump_dom(f"http://127.0.0.1:{server.server_port}/?no_hmr=1", 1500)
        assert result.returncode == 0, result.stderr
        assert "<title>7</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome/Chromium is not installed")
def test_npm_style_long_form_directives_render_in_real_chrome(tmp_path: Path):
    (tmp_path / "static" / "js").mkdir(parents=True)
    (tmp_path / "static" / "js" / "App.vel").write_text(
        '<template><button v-on:click="toggle">Toggle</button>'
        '<p v-if="visible">Visible</p>'
        '<ul><li v-for="(item, index) in items" v-bind:key="item.id">{{ index }}:{{ item.name }}</li></ul></template>'
        '<script>export default { data() { return { visible: true, items: [{id: 1, name: "A"}, {id: 2, name: "B"}] }; }, methods: { toggle() { this.visible = !this.visible; } } };</script>',
        encoding="utf-8",
    )
    build_project(tmp_path, options={"dev": True, "source_maps": False})
    (tmp_path / "dist" / "index.html").write_text(
        '<div id="app"></div><script type="module">import { mount } from "/static/js/App.js"; mount("#app"); '
        'setTimeout(() => { document.querySelector("button").click(); setTimeout(() => document.title = document.querySelector("p") ? "bad" : document.querySelector("ul").textContent, 50); }, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path / "dist")
    try:
        time.sleep(0.1)
        result = _dump_dom(f"http://127.0.0.1:{server.server_port}/?no_hmr=1", 1200)
        assert result.returncode == 0, result.stderr
        assert "<title>0:A1:B</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()
