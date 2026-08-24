"""Local, dependency-free debugger dashboard for Teloce projects.

The dashboard is intentionally localhost-only by default. It inspects project
structure and compiles discovered ``.vel`` files to show diagnostics; it does
not expose source contents or execute application code.
"""

from __future__ import annotations

import json
import platform
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from teloce.compiler import compile_file
from teloce.version import __version__


INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Teloce Debugger</title>
  <style>
    :root { color-scheme: dark; --bg:#0f172a; --panel:#172033; --line:#2c3a54; --text:#e5edf8; --muted:#91a2bd; --good:#34d399; --bad:#fb7185; --accent:#8b9cff; }
    * { box-sizing:border-box; } body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 system-ui,sans-serif; }
    header { padding:28px max(24px,calc((100% - 1180px)/2)); border-bottom:1px solid var(--line); display:flex; justify-content:space-between; align-items:center; gap:20px; }
    h1,h2,p { margin-top:0; } h1 { margin-bottom:4px; font-size:28px; } h2 { font-size:18px; }
    .muted { color:var(--muted); } main { max-width:1180px; margin:24px auto; padding:0 24px; }
    .actions { display:flex; gap:10px; } button { border:1px solid var(--line); border-radius:8px; padding:9px 14px; background:#202d48; color:var(--text); cursor:pointer; } button:hover { border-color:var(--accent); }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:14px; margin-bottom:20px; }
    .panel { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:18px; margin-bottom:20px; } .metric { font-size:28px; font-weight:700; } .label { color:var(--muted); }
    table { width:100%; border-collapse:collapse; } th,td { border-bottom:1px solid var(--line); padding:10px 8px; text-align:left; vertical-align:top; } th { color:var(--muted); font-weight:500; }
    .ok { color:var(--good); } .bad { color:var(--bad); } code { color:#c4b5fd; word-break:break-word; } .empty { color:var(--muted); padding:14px 0; }
    @media(max-width:600px) { header { display:block; } .actions { margin-top:15px; } }
  </style>
</head>
<body>
  <header><div><h1>Teloce Debugger</h1><div class="muted" id="subtitle">Loading project...</div></div><div class="actions"><button id="refresh">Refresh diagnostics</button></div></header>
  <main>
    <section class="grid" id="metrics"></section>
    <section class="panel"><h2>Project</h2><div id="project" class="muted">Loading...</div></section>
    <section class="panel"><h2>Component diagnostics</h2><div id="diagnostics" class="muted">Loading...</div></section>
  </main>
  <script>
    const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    async function load() {
      const [project, diagnostics] = await Promise.all([
        fetch('/api/project').then(r => r.json()),
        fetch('/api/diagnostics').then(r => r.json())
      ]);
      document.querySelector('#subtitle').textContent = `${project.name} · Teloce-Py ${project.version}`;
      document.querySelector('#metrics').innerHTML = [
        ['Components', diagnostics.total], ['Passing', diagnostics.passed], ['Errors', diagnostics.errors], ['Warnings', diagnostics.warnings]
      ].map(([label, value]) => `<div class="panel"><div class="metric ${label === 'Errors' && value ? 'bad' : ''}">${esc(value)}</div><div class="label">${esc(label)}</div></div>`).join('');
      document.querySelector('#project').innerHTML = `<p><strong>Root:</strong> <code>${esc(project.root)}</code></p><p><strong>Python:</strong> ${esc(project.python)}<br><strong>Platform:</strong> ${esc(project.platform)}</p><p><strong>Static directory:</strong> ${esc(project.static_dir || 'not found')}<br><strong>Templates directory:</strong> ${esc(project.templates_dir || 'not found')}</p>`;
      if (!diagnostics.results.length) { document.querySelector('#diagnostics').innerHTML = '<div class="empty">No .vel components were discovered.</div>'; return; }
      document.querySelector('#diagnostics').innerHTML = `<table><thead><tr><th>Component</th><th>Status</th><th>Errors</th><th>Warnings</th></tr></thead><tbody>${diagnostics.results.map(item => `<tr><td><code>${esc(item.file)}</code></td><td class="${item.success ? 'ok' : 'bad'}">${item.success ? 'Pass' : 'Fail'}</td><td>${item.errors.map(e => esc(e.message || e)).join('<br>') || '—'}</td><td>${item.warnings.map(e => esc(e.message || e)).join('<br>') || '—'}</td></tr>`).join('')}</tbody></table>`;
    }
    document.querySelector('#refresh').addEventListener('click', load);
    load().catch(error => { document.querySelector('#diagnostics').textContent = `Dashboard error: ${error.message}`; });
  </script>
</body>
</html>"""


def _json_safe(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return str(value)


class DebuggerDashboard:
    """Serve the local debugger UI and project inspection endpoints."""

    def __init__(self, root: str | Path, host: str = "localhost", port: int = 9000):
        self.root = Path(root).resolve()
        self.host = host
        self.port = port
        dashboard = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:
                return

            def _send(self, payload: Any, content_type: str = "application/json", status: int = 200) -> None:
                body = payload.encode("utf-8") if isinstance(payload, str) else json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", f"{content_type}; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self) -> None:  # noqa: N802
                route = urlsplit(self.path).path
                if route == "/":
                    self._send(INDEX_HTML, "text/html")
                elif route == "/api/health":
                    self._send({"ok": True, "service": "teloce-debugger", "version": __version__})
                elif route == "/api/project":
                    self._send(dashboard.project_info())
                elif route == "/api/diagnostics":
                    self._send(dashboard.diagnostics())
                else:
                    self._send({"error": "Not found"}, status=404)

        self.server = ThreadingHTTPServer((host, port), Handler)
        self.server.daemon_threads = True
        self._thread: threading.Thread | None = None

    @property
    def url(self) -> str:
        host = "127.0.0.1" if self.host in {"localhost", "0.0.0.0"} else self.host
        return f"http://{host}:{self.server.server_port}"

    def _vel_files(self) -> list[Path]:
        static = self.root / "static"
        search_root = static if static.exists() else self.root
        return sorted(path for path in search_root.rglob("*.vel") if path.is_file())[:500]

    def _relative(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def project_info(self) -> dict[str, Any]:
        static = self.root / "static"
        templates = self.root / "templates"
        return {
            "name": self.root.name,
            "root": str(self.root),
            "version": __version__,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "static_dir": str(static) if static.exists() else None,
            "templates_dir": str(templates) if templates.exists() else None,
            "components": [self._relative(path) for path in self._vel_files()],
        }

    def diagnostics(self) -> dict[str, Any]:
        results = []
        for path in self._vel_files():
            result = compile_file(path)
            diagnostics = result.get("diagnostics", {})
            errors = diagnostics.get("errors", [])
            warnings = diagnostics.get("warnings", [])
            results.append({
                "file": self._relative(path),
                "success": bool(result.get("success")),
                "errors": _json_safe(errors),
                "warnings": _json_safe(warnings),
            })
        return {
            "total": len(results),
            "passed": sum(1 for item in results if item["success"]),
            "errors": sum(len(item["errors"]) for item in results),
            "warnings": sum(len(item["warnings"]) for item in results),
            "results": results,
        }

    def start(self) -> None:
        self._thread = threading.Thread(target=self.server.serve_forever, name="teloce-debugger", daemon=True)
        self._thread.start()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
