from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np

from pc2sw.model import SwDocument


def write_sw(doc: SwDocument, path: str | Path, *, libver: str = "earliest") -> None:
    """
    Write a non-indexed .sw: only ``Header`` and ensemble groups with
    ``genomic_position/regions`` and ``spatial_position/t_*``.
    """
    path = Path(path)
    with h5py.File(path, "w", libver=libver) as dst:
        hg = dst.create_group("Header")
        for k, v in doc.header.attrs.items():
            hg.attrs[k] = v
        if "point_type" not in hg.attrs and "pointtype" not in hg.attrs:
            pm = doc.effective_point_mode()
            hg.attrs["point_type"] = "multi_point" if pm == "multi_point" else "single_point"

        for e in doc.ensembles:
            eg = dst.create_group(e.name)
            gp = eg.create_group("genomic_position")
            regions = _regions_for_write(e.regions)
            gp.create_dataset("regions", data=regions)

            sp = eg.create_group("spatial_position")
            for name in sorted(e.traces.keys(), key=_trace_sort_key):
                sp.create_dataset(name, data=np.asarray(e.traces[name], dtype=np.float64), dtype=np.float64)


def _trace_sort_key(name: str) -> tuple[int, str]:
    if name.startswith("t_") and name[2:].isdigit():
        return (int(name[2:]), name)
    return (10**9, name)


def _regions_for_write(regions: np.ndarray) -> np.ndarray:
    r = np.asarray(regions)
    if r.dtype != object:
        return r
    out = np.empty(r.shape, dtype=object)
    for idx in np.ndindex(r.shape):
        x = r[idx]
        if isinstance(x, bytes):
            out[idx] = x.decode("utf-8", errors="surrogateescape")
        elif x is None:
            out[idx] = ""
        else:
            out[idx] = str(x)
    return out
