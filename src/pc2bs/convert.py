from __future__ import annotations

import tempfile
from pathlib import Path

from pc2bs.read import read_sw
from pc2bs.transform import to_ballstick
from pc2bs.write import write_sw


def pointcloud_to_ballstick(
    src_path: str | Path,
    dst_path: str | Path,
    *,
    index: bool = True,
) -> None:
    """
    Read a point-cloud .sw, collapse spatial clusters to bbox centers, write
    a ball-and-stick .sw. When ``index`` is true, append an ``_index`` dataset
    via hdf5-indexer so jsfive-based readers (e.g. Spacewalk) can jump
    straight to datasets.
    """
    doc = read_sw(Path(src_path))
    if doc.effective_point_mode() != "multi_point":
        raise ValueError(
            "This tool only converts point-cloud .sw files to ball-and-stick. "
            "The input already looks like ball-and-stick (single_point / (R,3) traces)."
        )
    dst_path = Path(dst_path)
    write_sw(to_ballstick(doc), dst_path)
    if index:
        _append_index(dst_path)


def _append_index(path: Path) -> None:
    import hdf5_indexer

    hdf5_indexer.make_index(str(path))


def resolve_stdio_path(path: str, *, is_input: bool) -> tuple[str, tempfile.TemporaryDirectory | None]:
    if path != "-":
        return path, None
    tmp = tempfile.TemporaryDirectory(prefix="pc2bs-")
    name = "stdin.sw" if is_input else "stdout.sw"
    p = Path(tmp.name) / name
    if is_input:
        p.write_bytes(Path("/dev/stdin").read_bytes())
    return str(p), tmp
