from __future__ import annotations

import http.server
import threading
import time
import webbrowser
from importlib.resources import files
from pathlib import Path
from typing import Tuple

DEFAULT_SPACEWALK_URL = "https://aidenlab.org/spacewalk/"


def _load_launcher_template() -> str:
    return (files("pc2bs") / "assets" / "launcher.html").read_text(encoding="utf-8")


def _render_launcher(spacewalk_url: str, file_url: str, filename: str) -> bytes:
    html = (
        _load_launcher_template()
        .replace("__SPACEWALK_URL__", spacewalk_url)
        .replace("__FILE_URL__", file_url)
        .replace("__FILENAME__", filename)
    )
    return html.encode("utf-8")


def build_launcher_server(
    output_path: Path,
    *,
    spacewalk_url: str = DEFAULT_SPACEWALK_URL,
) -> Tuple[http.server.ThreadingHTTPServer, threading.Event, str]:
    """Construct an HTTP server that serves the launcher page and the output file.

    Returns (server, done_event, url). The caller is responsible for starting
    serve_forever on a thread and calling shutdown/server_close when finished.
    The done_event fires when the launcher page POSTs /done.
    """
    output_path = Path(output_path).resolve()
    if not output_path.is_file():
        raise FileNotFoundError(output_path)
    file_bytes = output_path.read_bytes()
    filename = output_path.name
    file_route = "/" + filename

    launcher_html = _render_launcher(spacewalk_url, file_route, filename)
    done = threading.Event()

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._send(200, "text/html; charset=utf-8", launcher_html)
            elif self.path == file_route:
                self._send(200, "application/octet-stream", file_bytes)
            else:
                self._send(404, "text/plain; charset=utf-8", b"not found")

        def do_POST(self):
            if self.path == "/done":
                self._send(204, "text/plain; charset=utf-8", b"")
                done.set()
            else:
                self._send(404, "text/plain; charset=utf-8", b"not found")

        def _send(self, code: int, ctype: str, body: bytes) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if body:
                self.wfile.write(body)

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    host, port = server.server_address[:2]
    url = f"http://{host}:{port}/"
    return server, done, url


def launch_in_spacewalk(
    output_path: Path,
    *,
    spacewalk_url: str = DEFAULT_SPACEWALK_URL,
    timeout: float = 120.0,
    open_browser: bool = True,
) -> bool:
    """Serve output_path locally and open a browser page that hands it off to Spacewalk.

    Returns True if the launcher reported a completed handoff, False on timeout.
    """
    server, done, url = build_launcher_server(output_path, spacewalk_url=spacewalk_url)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        if open_browser:
            opened = webbrowser.open(url)
            if not opened:
                print(f"pc2bs: open this URL in your browser: {url}")
        ok = done.wait(timeout=timeout)
        if ok:
            # Give the browser a moment to receive the 204 before we tear down.
            time.sleep(0.3)
        return ok
    finally:
        server.shutdown()
        server.server_close()
