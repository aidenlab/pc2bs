from __future__ import annotations

import copy

import numpy as np

from pc2bs.model import Ensemble, SwDocument, SwHeader, n_regions_from_regions


def _bbox_centroid(xyz: np.ndarray) -> np.ndarray:
    """Axis-aligned bounding box center (matches Spacewalk mathUtils)."""
    if xyz.size == 0:
        return np.array([np.nan, np.nan, np.nan], dtype=np.float64)
    valid = ~np.isnan(xyz).any(axis=1)
    if not np.any(valid):
        return np.array([np.nan, np.nan, np.nan], dtype=np.float64)
    sub = xyz[valid]
    lo = sub.min(axis=0)
    hi = sub.max(axis=0)
    return (lo + hi) / 2.0


def _collapse_trace_to_ballstick(trace: np.ndarray, n_reg: int) -> np.ndarray:
    t = np.asarray(trace, dtype=np.float64)
    if t.ndim == 1:
        t = t.reshape(-1, 4)
    out = np.full((n_reg, 3), np.nan, dtype=np.float64)
    if t.size == 0:
        return out
    ri = np.rint(t[:, 0]).astype(np.int64)
    xyz = t[:, 1:4]
    for ridx in range(n_reg):
        mask = ri == ridx
        if np.any(mask):
            out[ridx] = _bbox_centroid(xyz[mask])
    return out


def _header_with_point_type(header: SwHeader) -> SwHeader:
    d = copy.deepcopy(dict(header.attrs))
    d["point_type"] = "single_point"
    return SwHeader(attrs=d)


def to_ballstick(doc: SwDocument) -> SwDocument:
    """Point cloud → ball-and-stick (new document)."""
    if doc.effective_point_mode() != "multi_point":
        return doc
    new_ensembles: list[Ensemble] = []
    for e in doc.ensembles:
        n_reg = n_regions_from_regions(e.regions)
        traces = {name: _collapse_trace_to_ballstick(arr, n_reg) for name, arr in e.traces.items()}
        new_ensembles.append(
            Ensemble(
                name=e.name,
                regions=e.regions,
                traces=traces,
                inferred_mode="single_point",
            )
        )
    return SwDocument(
        header=_header_with_point_type(doc.header),
        ensembles=tuple(new_ensembles),
    )
