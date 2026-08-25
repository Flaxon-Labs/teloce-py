"""Real-browser router validation."""

import subprocess
import tempfile
import time
from pathlib import Path

import pytest

from teloce.cli.server import start_dev_server
from teloce.router.compiler import RouterCompiler
from teloce.router.generator import RouterGenerator


def _chrome() -> str | None:
    candidate = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    return str(candidate) if candidate.exists() else None


def _dump_dom(url: str):
    with tempfile.TemporaryDirectory(prefix="teloce-router-chrome-") as profile:
        return subprocess.run(
            [_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu",
             "--disable-extensions", "--no-first-run", "--no-default-browser-check",
             f"--user-data-dir={profile}", "--dump-dom", "--virtual-time-budget=1500", url],
            capture_output=True, text=True, timeout=20,
        )


@pytest.mark.skipif(_chrome() is None, reason="Chrome is not installed")
def test_generated_router_navigates_params_and_updates_view(tmp_path: Path):
    config = RouterCompiler().compile({
        "routes": [
            {"path": "/", "component": "Home"},
            {"path": "/users/:id", "component": "User"},
            {"path": "/docs/*", "component": "Docs"},
            {"path": "/posts/:slug?", "component": "Posts"},
        ]
    })
    (tmp_path / "Router.js").write_text(
        'const Home = "Home"; const User = "User"; const Docs = "Docs"; const Posts = "Posts";\n'
        + RouterGenerator().generate(config)
        + "\nwindow.__router = router;",
        encoding="utf-8",
    )
    (tmp_path / "view.js").write_text(
        'export const createRouterView = (router, container, render) => { '
        'const update = () => render(router.state.route?.component, router.state, container); '
        'router.subscribe(update); update(); return { update }; };',
        encoding="utf-8",
    )
    (tmp_path / "index.html").write_text(
        '<div id="app"></div><script>window.onerror = (message) => document.title = "ERR:" + message;</script><script type="module">'
        'import router from "/Router.js"; import { createRouterView } from "/view.js"; '
        'createRouterView(router, document.querySelector("#app"), (component, state, container) => { '
        'container.textContent = component; }); '
        'setTimeout(async () => { try { await router.push("/users/42?tab=posts"); '
        'setTimeout(() => { const wildcard = router.resolve("/docs/a/b"); const optional = router.resolve("/posts"); document.title = router.currentRoute().component + ":" + router.params().id + ":" + router.query().tab + ":" + wildcard.params.pathMatch + ":" + (optional.params.slug === undefined ? "none" : optional.params.slug); }, 50); '
        '} catch (error) { document.title = "ERR:" + error.message; } }, 50);'
        '</script>',
        encoding="utf-8",
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path, hmr=False)
    try:
        time.sleep(0.1)
        result = _dump_dom(f"http://127.0.0.1:{server.server_port}/?no_hmr=1")
        assert result.returncode == 0, result.stderr
        assert "<title>User:42:posts:a/b:none</title>" in result.stdout
    finally:
        server.shutdown()
        server.server_close()
