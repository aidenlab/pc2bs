from __future__ import annotations

import re
from typing import Literal

import h5py

PointMode = Literal["multi_point", "single_point"]


def _decode_attr(val) -> str:
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    if isinstance(val, (str, int, float)):
        return str(val)
    try:
        return val.decode("utf-8")  # type: ignore[attr-defined]
    except Exception:
        return str(val)


def header_group(f: h5py.File) -> h5py.Group | None:
    if "Header" in f:
        return f["Header"]
    if "header" in f:
        return f["header"]
    return None


def read_point_mode(f: h5py.File) -> PointMode | None:
    hg = header_group(f)
    if hg is None:
        return None
    for key in ("point_type", "pointtype"):
        if key in hg.attrs:
            raw = _decode_attr(hg.attrs[key]).lower().strip()
            if raw == "multi_point":
                return "multi_point"
            if raw in ("single_point", "single-point", "single"):
                return "single_point"
    return None


def infer_point_mode_from_trace(f: h5py.File, ensemble_key: str) -> PointMode:
    sp = f[ensemble_key]["spatial_position"]
    names = trace_dataset_names(sp)
    if not names:
        raise ValueError(f"No spatial_position traces in ensemble {ensemble_key!r}")
    ds = sp[names[0]]
    arr = ds[()]
    if arr.ndim == 1:
        n = arr.size
        if n % 4 == 0:
            return "multi_point"
        if n % 3 == 0:
            return "single_point"
        raise ValueError(f"Trace {names[0]!r} length {n} is not a multiple of 3 or 4")
    if arr.ndim == 2:
        c = arr.shape[1]
        if c == 4:
            return "multi_point"
        if c == 3:
            return "single_point"
    raise ValueError(f"Unsupported trace shape {arr.shape} for {names[0]!r}")


def trace_dataset_names(spatial_position: h5py.Group) -> list[str]:
    pat = re.compile(r"^t_(\d+)$")
    found: list[tuple[int, str]] = []
    for name in spatial_position.keys():
        m = pat.match(name)
        if m and isinstance(spatial_position[name], h5py.Dataset):
            found.append((int(m.group(1)), name))
    found.sort(key=lambda x: x[0])
    return [n for _, n in found]


def ensemble_keys(f: h5py.File) -> list[str]:
    skip = {"Header", "header", "_index"}
    return [
        k
        for k in f.keys()
        if k not in skip
        and isinstance(f[k], h5py.Group)
        and "genomic_position" in f[k]
        and "spatial_position" in f[k]
    ]


def n_regions(f: h5py.File, ensemble_key: str) -> int:
    regions = f[ensemble_key]["genomic_position"]["regions"]
    r = regions.shape
    if len(r) == 2 and r[1] == 3:
        return int(r[0])
    if len(r) == 1:
        n = int(r[0])
        if n % 3 != 0:
            raise ValueError("regions dataset length is not a multiple of 3")
        return n // 3
    raise ValueError(f"Unexpected regions shape {r}")
