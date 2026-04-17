from __future__ import annotations

import tempfile
from pathlib import Path

from pc2bs.read import read_sw
from pc2bs.transform import to_ballstick
from pc2bs.write import write_sw


def pointcloud_to_ballstick(src_path: str | Path, dst_path: str | Path) -> None:
    """
    Read a point-cloud .sw, collapse spatial clusters to bbox centers, write
    a non-indexed ball-and-stick .sw.
    """
    doc = read_sw(Path(src_path))
    if doc.effective_point_mode() != "multi_point":
        raise ValueError(
            "This tool only converts point-cloud .sw files to ball-and-stick. "
            "The input already looks like ball-and-stick (single_point / (R,3) traces)."
        )
    write_sw(to_ballstick(doc), Path(dst_path))


def resolve_stdio_path(path: str, *, is_input: bool) -> tuple[str, tempfile.TemporaryDirectory | None]:
    if path != "-":
        return path, None
    tmp = tempfile.TemporaryDirectory(prefix="pc2bs-")
    name = "stdin.sw" if is_input else "stdout.sw"
    p = Path(tmp.name) / name
    if is_input:
        p.write_bytes(Path("/dev/stdin").read_bytes())
    return str(p), tmp
