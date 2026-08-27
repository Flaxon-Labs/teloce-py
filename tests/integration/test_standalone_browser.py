"""Real browser coverage for npm/CDN-style standalone Teloce usage."""

import shutil
import subprocess
import time
from pathlib import Path

import pytest

from teloce.cli.server import start_dev_server


_subprocess_run = subprocess.run


def _stable_chrome_run(command, *args, **kwargs):
    """Make repeated Windows headless-Chrome launches deterministic."""
    command = list(command)
    if "--headless=new" not in command:
        return _subprocess_run(command, *args, **kwargs)
    for flag in (
        "--disable-software-rasterizer",
        "--disable-extensions",
        "--disable-sync",
        "--disable-background-networking",
        "--disable-component-update",
        "--no-first-run",
        "--no-default-browser-check",
    ):
        if flag not in command:
            command.insert(1, flag)
    kwargs["timeout"] = min(kwargs.get("timeout", 60), 30)
    failure = None
    for _attempt in range(2):
        try:
            return _subprocess_run(command, *args, **kwargs)
        except subprocess.TimeoutExpired as error:
            failure = error
    raise failure


subprocess.run = _stable_chrome_run


def _chrome() -> str | None:
    candidate = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    return str(candidate) if candidate.exists() else None


@pytest.mark.skipif(_chrome() is None, reason="Chrome is not installed")
def test_standalone_create_app_reacts_to_events_in_real_chrome(tmp_path: Path):
    shutil.copy(Path(__file__).parents[2] / "src/teloce/runtime/standalone.js", tmp_path / "teloce.js")
    (tmp_path / "index.html").write_text(
        '<div id="app"><h1>{{ name }}</h1><button @click="count++">{{ count }}</button></div>'
        '<script src="/teloce.js"></script><script>teloce.createApp("#app", {name: "Python", count: 0}); '
        'setTimeout(() => { document.querySelector("button").click(); setTimeout(() => document.title = document.querySelector("button").textContent, 50); }, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path, hmr=False)
    try:
        time.sleep(0.1)
        result = subprocess.run(
            [_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu",
             "--disable-software-rasterizer", "--disable-extensions", "--disable-sync",
             "--disable-background-networking", "--disable-component-update",
             "--no-first-run", "--no-default-browser-check", "--dump-dom",
             "--virtual-time-budget=1000", f"http://127.0.0.1:{server.server_port}/?no_hmr=1"],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, result.stderr
        assert "<title>1</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome is not installed")
def test_standalone_invokes_event_methods_with_state_context(tmp_path: Path):
    runtime = Path(__file__).parents[2].joinpath("src", "teloce", "runtime", "standalone.js")
    (tmp_path / "teloce.js").write_text(runtime.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "index.html").write_text(
        '<div id="app"><button @click="increment">{{ count }}</button></div>'
        '<script src="/teloce.js"></script><script>teloce.createApp("#app", { count: 0, increment() { this.count += 1; } });'
        'setTimeout(() => { document.querySelector("button").click(); setTimeout(() => document.title = document.querySelector("button").textContent, 50); }, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path, hmr=False)
    try:
        time.sleep(0.1)
        result = subprocess.run(
            [_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu",
             "--disable-software-rasterizer", "--disable-extensions", "--disable-sync",
             "--disable-background-networking", "--disable-component-update",
             "--no-first-run", "--no-default-browser-check", "--dump-dom",
             "--virtual-time-budget=1200", f"http://127.0.0.1:{server.server_port}/"],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, result.stderr
        assert "<title>1</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome/Chromium is not installed")
def test_standalone_supports_npm_style_directives(tmp_path: Path):
    (tmp_path / "teloce.js").write_text(
        Path(__file__).parents[2].joinpath("src", "teloce", "runtime", "standalone.js").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / "index.html").write_text(
        '<div id="app"><p v-if="visible">Visible</p><strong>{{ name | capitalize }}</strong>'
        '<span v-for="(item, index) in items">{{ index }}:{{ item }}</span></div>'
        '<script src="/teloce.js"></script><script>teloce.createApp("#app", { visible: false, name: "hello world", items: ["A", "B"] });'
        'setTimeout(() => document.title = document.querySelector("#app").textContent, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path, hmr=False)
    try:
        time.sleep(0.1)
        result = subprocess.run(
            [_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu", "--dump-dom",
             "--virtual-time-budget=1200", f"http://127.0.0.1:{server.server_port}/"],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, result.stderr
        assert "Hello world0:A1:B" in result.stdout
        assert "Visible" not in result.stdout.split("<title>", 1)[-1].split("</title>", 1)[0]
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome/Chromium is not installed")
def test_standalone_plugin_directive_runs_render_hook_in_real_chrome(tmp_path: Path):
    (tmp_path / "teloce.js").write_text(
        Path(__file__).parents[2].joinpath("src", "teloce", "runtime", "standalone.js").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / "index.html").write_text(
        '<div id="app"><p v-highlight="name">original</p></div>'
        '<script src="/teloce.js"></script><script>teloce.use({ directives: [{ name: "highlight", render(el, binding) { el.textContent = binding.value.toUpperCase(); } }] });'
        'teloce.createApp("#app", { name: "plugin works" }); setTimeout(() => document.title = document.querySelector("p").textContent, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path, hmr=False)
    try:
        time.sleep(0.1)
        result = subprocess.run(
            [_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu", "--dump-dom",
             "--virtual-time-budget=1000", f"http://127.0.0.1:{server.server_port}/"],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, result.stderr
        assert "<title>PLUGIN WORKS</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome is not installed")
def test_standalone_supports_v_else_if_and_v_else(tmp_path: Path):
    runtime = Path(__file__).parents[2].joinpath("src", "teloce", "runtime", "standalone.js")
    (tmp_path / "teloce.js").write_text(runtime.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "index.html").write_text(
        '<div id="app"><p v-if="first">first</p><p v-else-if="second">second</p><p v-else>fallback</p></div>'
        '<script src="/teloce.js"></script><script>teloce.createApp("#app", { first: false, second: true });'
        'setTimeout(() => document.title = document.querySelector("#app").textContent, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path, hmr=False)
    try:
        time.sleep(0.1)
        result = subprocess.run(
            [_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu", "--dump-dom",
             "--virtual-time-budget=1000", f"http://127.0.0.1:{server.server_port}/"],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, result.stderr
        assert "<title>second</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome is not installed")
def test_standalone_supports_v_model_alias_and_selects(tmp_path: Path):
    runtime = Path(__file__).parents[2].joinpath("src", "teloce", "runtime", "standalone.js")
    (tmp_path / "teloce.js").write_text(runtime.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "index.html").write_text(
        '<div id="app"><input v-model="name"><select v-model="choice"><option value="b">B</option></select><p>{{ name }}:{{ choice }}</p></div>'
        '<script src="/teloce.js"></script><script>teloce.createApp("#app", { name: "A", choice: "a" });'
        'setTimeout(() => { const input = document.querySelector("input"); input.value = "C"; input.dispatchEvent(new Event("input", {bubbles: true})); const select = document.querySelector("select"); select.value = "b"; select.dispatchEvent(new Event("change", {bubbles: true})); setTimeout(() => document.title = document.querySelector("p").textContent, 50); }, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path, hmr=False)
    try:
        time.sleep(0.1)
        result = subprocess.run(
            [_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu", "--dump-dom",
             "--virtual-time-budget=1200", f"http://127.0.0.1:{server.server_port}/"],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, result.stderr
        assert "<title>C:b</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome is not installed")
def test_standalone_reacts_to_nested_objects_and_arrays(tmp_path: Path):
    runtime = Path(__file__).parents[2].joinpath("src", "teloce", "runtime", "standalone.js")
    (tmp_path / "teloce.js").write_text(runtime.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "index.html").write_text(
        '<div id="app"><p>{{ user.name }}:{{ items.length }}</p><button @click="(user.name = \'B\', items.push(2))">Change</button></div>'
        '<script src="/teloce.js"></script><script>teloce.createApp("#app", { user: { name: "A" }, items: [1] });'
        'setTimeout(() => { document.querySelector("button").click(); setTimeout(() => document.title = document.querySelector("p").textContent, 50); }, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path, hmr=False)
    try:
        time.sleep(0.1)
        result = subprocess.run(
            [_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu", "--dump-dom",
             "--virtual-time-budget=1500", f"http://127.0.0.1:{server.server_port}/"],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, result.stderr
        assert "<title>B:2</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.skipif(_chrome() is None, reason="Chrome is not installed")
def test_standalone_plugin_component_renders_props(tmp_path: Path):
    runtime = Path(__file__).parents[2].joinpath("src", "teloce", "runtime", "standalone.js")
    (tmp_path / "teloce.js").write_text(runtime.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "index.html").write_text(
        '<div id="app"><Badge label="Ready"></Badge><p>{{ hello() }}</p></div>'
        '<script src="/teloce.js"></script><script>teloce.use({ helpers: { hello() { return "works"; } }, components: { Badge: { render(el, props) { return "<strong>" + props.label + "</strong>"; } } } });'
        'teloce.createApp("#app", {}); setTimeout(() => document.title = document.querySelector("strong").textContent + ":" + document.querySelector("p").textContent, 50);</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path, hmr=False)
    try:
        time.sleep(0.1)
        result = subprocess.run(
            [_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu", "--dump-dom",
             "--virtual-time-budget=1000", f"http://127.0.0.1:{server.server_port}/"],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, result.stderr
        assert "<title>Ready:works</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()
