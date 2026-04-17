from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np

from pc2bs.layout import ensemble_keys, header_group, infer_point_mode_from_trace, read_point_mode, trace_dataset_names
from pc2bs.model import Ensemble, SwDocument, SwHeader, n_regions_from_regions


def read_sw(path: str | Path) -> SwDocument:
    """Load a .sw file into :class:`SwDocument` (ignores index-only root objects)."""
    path = Path(path)
    with h5py.File(path, "r") as f:
        names = ensemble_keys(f)
        if not names:
            raise ValueError("No ensemble groups with genomic_position and spatial_position found")

        hg = header_group(f)
        attrs: dict = {}
        if hg is not None:
            for k in hg.attrs:
                attrs[k] = hg.attrs[k]

        declared = read_point_mode(f)
        ensembles: list[Ensemble] = []
        for ek in names:
            inferred = infer_point_mode_from_trace(f, ek)
            if declared is not None and inferred != declared:
                raise ValueError(
                    f"Ensemble {ek!r}: Header declares {declared} but traces look like {inferred}"
                )
            g = f[ek]
            regions = g["genomic_position"]["regions"][()]
            regions = np.asarray(regions)
            n_reg = n_regions_from_regions(regions)
            sp = g["spatial_position"]
            trace_names = trace_dataset_names(sp)
            traces: dict[str, np.ndarray] = {}
            for tn in trace_names:
                arr = np.asarray(sp[tn][()], dtype=np.float64)
                traces[tn] = _validate_trace_shape(arr, inferred, n_reg, tn)
            ensembles.append(
                Ensemble(
                    name=ek,
                    regions=regions,
                    traces=traces,
                    inferred_mode=inferred,
                )
            )

        modes = {e.inferred_mode for e in ensembles}
        if len(modes) > 1:
            raise ValueError(f"Ensembles disagree on point layout: {modes}")

        return SwDocument(header=SwHeader(attrs=attrs), ensembles=tuple(ensembles))


def _validate_trace_shape(
    arr: np.ndarray, mode: PointMode, n_reg: int, trace_name: str
) -> np.ndarray:
    if mode == "single_point":
        a = _as_single(arr)
        if a.shape[0] != n_reg:
            raise ValueError(
                f"Trace {trace_name}: ball-and-stick rows {a.shape[0]} != regions rows {n_reg}"
            )
        return a
    a = _as_multi(arr)
    return a


def _as_multi(raw: np.ndarray) -> np.ndarray:
    a = np.asarray(raw, dtype=np.float64)
    if a.ndim == 1:
        if a.size % 4 != 0:
            raise ValueError("Point-cloud trace flat length is not a multiple of 4")
        return a.reshape(-1, 4)
    if a.ndim == 2 and a.shape[1] == 4:
        return a
    raise ValueError(f"Expected point-cloud trace (N,4) or flat 4N; got shape {a.shape}")


def _as_single(raw: np.ndarray) -> np.ndarray:
    a = np.asarray(raw, dtype=np.float64)
    if a.ndim == 1:
        if a.size % 3 != 0:
            raise ValueError("Ball-and-stick trace flat length is not a multiple of 3")
        return a.reshape(-1, 3)
    if a.ndim == 2 and a.shape[1] == 3:
        return a
    raise ValueError(f"Expected ball-and-stick trace (R,3) or flat 3R; got shape {a.shape}")
