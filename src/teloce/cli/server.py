"""Dependency-free development server with SSE reload notifications."""

from __future__ import annotations

import queue
import threading
import base64
import hashlib
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


class _Handler(SimpleHTTPRequestHandler):
    server_version = "TeloceDev/1.0"

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server, directory=server.directory)

    def do_GET(self):  # noqa: N802 - stdlib handler API
        request_url = urlsplit(self.path)
        request_path = request_url.path
        request_query = request_url.query
        if request_path == "/__teloce_hmr":
            if self.headers.get("Upgrade", "").lower() == "websocket":
                self._serve_websocket()
                return
            self._serve_events()
            return
        if request_path == "/":
            self.path = "/index.html"
        if urlsplit(self.path).path.endswith(".html"):
            candidate = Path(self.server.directory) / urlsplit(self.path).path.lstrip("/")
            if candidate.is_file():
                body = candidate.read_text(encoding="utf-8")
                client = '' if 'no_hmr=1' in request_query or not self.server.hmr else '<script>(function(){const reload=()=>{if(window.__teloce_hmr_reload) window.__teloce_hmr_reload().catch(()=>location.reload()); else location.reload();};if(window.WebSocket){const ws=new WebSocket((location.protocol==="https:"?"wss://":"ws://")+location.host+"/__teloce_hmr");ws.onmessage=reload;ws.onerror=()=>{const s=new EventSource("/__teloce_hmr");s.addEventListener("reload",reload);};}else{const s=new EventSource("/__teloce_hmr");s.addEventListener("reload",reload);}})();</script>'
                body = body.replace("</body>", client + "</body>")
                data = body.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
        candidate = Path(self.server.directory) / urlsplit(self.path).path.lstrip("/")
        if not candidate.is_file() and self.server.proxy_target:
            self._proxy("GET")
            return
        super().do_GET()

    def do_POST(self):  # noqa: N802 - stdlib handler API
        if self.server.proxy_target:
            self._proxy("POST")
            return
        self.send_error(404)

    def _proxy(self, method: str):
        target = self.server.proxy_target.rstrip("/") + self.path
        body = None
        if method == "POST":
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
        request = Request(target, data=body, method=method)
        for name, value in self.headers.items():
            if name.lower() not in {"host", "content-length"}:
                request.add_header(name, value)
        try:
            with urlopen(request, timeout=30) as response:
                payload = response.read()
                self.send_response(response.status)
                for name, value in response.headers.items():
                    if name.lower() not in {"connection", "transfer-encoding"}:
                        self.send_header(name, value)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
        except HTTPError as error:
            self.send_response(error.code)
            self.end_headers()
            self.wfile.write(error.read())
        except URLError as error:
            self.send_error(502, f"Backend proxy failed: {error.reason}")

    def _serve_events(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        self.wfile.write(b": connected\n\n")
        self.wfile.flush()
        subscriber = queue.Queue()
        self.server.subscribe(subscriber)
        try:
            while True:
                try:
                    event = subscriber.get(timeout=15)
                    payload = f"event: {event}\ndata: {{}}\n\n".encode()
                except queue.Empty:
                    payload = b": keepalive\n\n"
                self.wfile.write(payload)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return
        finally:
            self.server.unsubscribe(subscriber)

    def _serve_websocket(self):
        """Serve a minimal text WebSocket transport for browser HMR."""
        key = self.headers.get("Sec-WebSocket-Key")
        if not key:
            self.send_error(400, "Missing Sec-WebSocket-Key")
            return
        accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
        self.send_response(101, "Switching Protocols")
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", accept)
        self.end_headers()
        subscriber = queue.Queue()
        self.server.subscribe(subscriber)
        try:
            while True:
                try:
                    event = subscriber.get(timeout=15)
                except queue.Empty:
                    event = "ping"
                payload = event.encode("utf-8")
                if len(payload) < 126:
                    self.connection.sendall(bytes([0x81, len(payload)]) + payload)
                else:
                    self.connection.sendall(bytes([0x81, 126]) + len(payload).to_bytes(2, "big") + payload)
        except (BrokenPipeError, ConnectionResetError, OSError):
            return
        finally:
            self.server.unsubscribe(subscriber)

    def log_message(self, format, *args):
        if getattr(self.server, "logging", True):
            super().log_message(format, *args)


class TeloceDevServer(ThreadingHTTPServer):
    """Serve the built application and broadcast rebuild events over SSE."""

    allow_reuse_address = True

    def __init__(self, host: str, port: int, directory: Path, logging: bool = True, proxy_target: str | None = None, hmr: bool = True):
        handler = type("TeloceRequestHandler", (_Handler,), {})
        handler.directory = str(directory)
        super().__init__((host, port), handler)
        self.directory = str(directory.resolve())
        self.proxy_target = proxy_target
        self.hmr = hmr
        self.subscribers: list[queue.Queue[str]] = []
        self._subscribers_lock = threading.Lock()
        self.logging = logging

    def subscribe(self, subscriber: queue.Queue[str]):
        with self._subscribers_lock:
            self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber: queue.Queue[str]):
        with self._subscribers_lock:
            if subscriber in self.subscribers:
                self.subscribers.remove(subscriber)

    def notify_reload(self):
        with self._subscribers_lock:
            for subscriber in list(self.subscribers):
                subscriber.put("reload")


def start_dev_server(host: str, port: int, directory: Path, proxy_target: str | None = None, hmr: bool = True) -> TeloceDevServer:
    server = TeloceDevServer(host, port, directory, proxy_target=proxy_target, hmr=hmr)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
