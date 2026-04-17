from __future__ import annotations

import threading
import urllib.request
from pathlib import Path

from pc2bs.launch import build_launcher_server


def test_launcher_server(tmp_path: Path) -> None:
    sw = tmp_path / "out.sw"
    payload = b"not-really-hdf5-but-fine-for-the-test"
    sw.write_bytes(payload)

    server, done, url = build_launcher_server(
        sw, spacewalk_url="https://example.invalid/spacewalk/"
    )
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        html = urllib.request.urlopen(url).read().decode("utf-8")
        assert "https://example.invalid/spacewalk/" in html
        assert "out.sw" in html
        assert "__SPACEWALK_URL__" not in html
        assert "__FILE_URL__" not in html
        assert "__FILENAME__" not in html

        body = urllib.request.urlopen(url + "out.sw").read()
        assert body == payload

        req = urllib.request.Request(url + "done", method="POST")
        resp = urllib.request.urlopen(req)
        assert resp.status == 204
        assert done.wait(timeout=1.0)
    finally:
        server.shutdown()
        server.server_close()
