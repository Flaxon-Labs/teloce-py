"""Development server integration tests."""

import threading
import time
import base64
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen

from teloce.cli.server import start_dev_server
from teloce.build import build_project


def test_dev_server_serves_html_and_hmr_endpoint(tmp_path: Path):
    (tmp_path / "index.html").write_text(
        "<!doctype html><body><main>App</main></body>", encoding="utf-8"
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path)
    try:
        address = f"http://127.0.0.1:{server.server_port}"
        with urlopen(address + "/", timeout=2) as response:
            html = response.read().decode()
        assert "App" in html
        assert "/__teloce_hmr" in html

        # Connect to SSE in a reader thread, then broadcast a rebuild event.
        received = []

        def read_event():
            with urlopen(address + "/__teloce_hmr", timeout=4) as response:
                while len(received) == 0:
                    line = response.readline().decode()
                    if "event: reload" in line:
                        received.append(line)

        reader = threading.Thread(target=read_event, daemon=True)
        reader.start()
        time.sleep(0.1)
        server.notify_reload()
        reader.join(timeout=2)
        assert received == ["event: reload\n"]
    finally:
        server.shutdown()
        server.server_close()


def test_dev_server_preserves_no_hmr_query_when_normalizing_root(tmp_path: Path):
    (tmp_path / "index.html").write_text(
        "<!doctype html><body><main>App</main></body>", encoding="utf-8"
    )
    server = start_dev_server("127.0.0.1", 0, tmp_path)
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/?no_hmr=1", timeout=2) as response:
            html = response.read().decode()
        assert "App" in html
        assert "/__teloce_hmr" not in html
    finally:
        server.shutdown()
        server.server_close()


def test_dev_build_materializes_framework_static_entrypoint(tmp_path: Path):
    (tmp_path / "templates").mkdir()
    (tmp_path / "static" / "js").mkdir(parents=True)
    (tmp_path / "templates" / "index.html").write_text(
        '<div id="app"></div><script type="module">import { mount } from "{{ url_for(\'static\', filename=\'js/App.js\') }}"; mount("#app");</script>',
        encoding="utf-8",
    )
    (tmp_path / "static" / "js" / "App.vel").write_text(
        "<template><div>ok</div></template>", encoding="utf-8"
    )
    build_project(tmp_path, options={"dev": True, "source_maps": False})
    entrypoint = (tmp_path / "dist" / "index.html").read_text(encoding="utf-8")
    assert "/static/js/App.js" in entrypoint
    assert "url_for" not in entrypoint


def test_dev_server_proxies_backend_api_requests(tmp_path: Path):
    class Backend(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

        def log_message(self, *_args):
            pass

    backend = ThreadingHTTPServer(("127.0.0.1", 0), Backend)
    threading.Thread(target=backend.serve_forever, daemon=True).start()
    server = start_dev_server(
        "127.0.0.1", 0, tmp_path,
        proxy_target=f"http://127.0.0.1:{backend.server_port}",
    )
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/api/health", timeout=2) as response:
            assert response.read() == b'{"ok":true}'
    finally:
        server.shutdown()
        server.server_close()
        backend.shutdown()
        backend.server_close()


def test_dev_server_websocket_hmr_transport(tmp_path: Path):
    server = start_dev_server("127.0.0.1", 0, tmp_path)
    client = socket.create_connection(("127.0.0.1", server.server_port), timeout=3)
    try:
        key = base64.b64encode(os.urandom(16)).decode()
        client.sendall((
            f"GET /__teloce_hmr HTTP/1.1\r\nHost: localhost\r\n"
            f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        ).encode())
        assert b"101 Switching Protocols" in client.recv(1024)
        time.sleep(0.05)
        server.notify_reload()
        assert b"reload" in client.recv(32)
    finally:
        client.close()
        server.shutdown()
        server.server_close()
