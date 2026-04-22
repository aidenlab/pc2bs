from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np

from pc2bs.model import SwDocument


# Bake format version written into Header.live_contact_map_vertices_version.
# Must match the version hic-straw's loadLiveVertices expects.
LIVE_CONTACT_MAP_VERTICES_VERSION = 1


def write_sw(doc: SwDocument, path: str | Path, *, libver: str = "earliest") -> None:
    """
    Write a non-indexed .sw: ``Header``, ensemble groups with
    ``genomic_position/regions`` and ``spatial_position/t_*``, plus the
    ``live_contact_map_vertices`` bake for single-point ensembles.

    The bake is a single dataset of shape (trace_count, trace_length, 3),
    float32, NaN for missing. It collapses what would otherwise be N per-trace
    HDF5 range reads into one, which matters for remote hosts (hic-straw reads
    it as a fast path when present).
    """
    path = Path(path)
    with h5py.File(path, "w", libver=libver) as dst:
        hg = dst.create_group("Header")
        for k, v in doc.header.attrs.items():
            hg.attrs[k] = v
        if "point_type" not in hg.attrs and "pointtype" not in hg.attrs:
            pm = doc.effective_point_mode()
            hg.attrs["point_type"] = "multi_point" if pm == "multi_point" else "single_point"

        bake_written = False
        for e in doc.ensembles:
            eg = dst.create_group(e.name)
            gp = eg.create_group("genomic_position")
            regions = _regions_for_write(e.regions)
            gp.create_dataset("regions", data=regions)

            sp = eg.create_group("spatial_position")
            trace_names = sorted(e.traces.keys(), key=_trace_sort_key)
            for name in trace_names:
                sp.create_dataset(name, data=np.asarray(e.traces[name], dtype=np.float64), dtype=np.float64)

            bake = _bake_live_contact_map_vertices(e.traces, trace_names)
            if bake is not None:
                eg.create_dataset("live_contact_map_vertices", data=bake, dtype=np.float32)
                bake_written = True

        if bake_written:
            hg.attrs["live_contact_map_vertices_version"] = LIVE_CONTACT_MAP_VERTICES_VERSION


def _bake_live_contact_map_vertices(traces: dict[str, np.ndarray], trace_names: list[str]):
    """
    Stack ball-and-stick traces into a single (trace_count, trace_length, 3)
    float32 array matching hic-straw loadLiveVertices v1. Returns None if
    the traces are not in ball-and-stick shape (e.g. multi_point pointclouds).
    """
    if not trace_names:
        return None

    shape0 = np.asarray(traces[trace_names[0]]).shape
    if len(shape0) != 2 or shape0[1] != 3:
        return None  # pointcloud or unexpected layout — skip bake

    stacked = np.stack(
        [np.asarray(traces[n], dtype=np.float32) for n in trace_names],
        axis=0,
    )
    return stacked


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
