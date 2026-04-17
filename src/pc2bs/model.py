"""
In-memory representation of the subset of .sw (HDF5) Spacewalk uses.

The published CLI only converts point cloud → ball-and-stick; this model still
describes both layouts because the reader must recognize them.

Contract (v1):
- Top-level ``Header`` group with string-like attributes; ``point_type`` is
  ``multi_point`` or ``single_point`` after write.
- ``live_contact_map_vertices`` and similar optional datasets are intentionally
  out of scope and are not read or written.
- Each ensemble is a top-level group with ``genomic_position/regions`` (R, 3)
  variable-length UTF-8 strings (chrom, start bp, end bp as text) and
  ``spatial_position`` datasets named ``t_<n>`` with float64 data:
  point cloud (N, 4) or flat 4N [region, x, y, z, ...]; ball-and-stick (R, 3)
  or flat 3N one row per genomic region.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

PointMode = Literal["multi_point", "single_point"]


@dataclass(frozen=True)
class SwHeader:
    """HDF5 ``/Header`` attributes as a plain mapping (h5py-compatible values)."""

    attrs: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Ensemble:
    """One experiment / sample group (e.g. ``PGP1``)."""

    name: str
    regions: np.ndarray
    traces: dict[str, np.ndarray]
    inferred_mode: PointMode


@dataclass(frozen=True)
class SwDocument:
    header: SwHeader
    ensembles: tuple[Ensemble, ...]

    def effective_point_mode(self) -> PointMode:
        for key in ("point_type", "pointtype"):
            if key in self.header.attrs:
                raw = _attr_to_str(self.header.attrs[key]).lower().strip()
                if raw == "multi_point":
                    return "multi_point"
                if raw in ("single_point", "single-point", "single"):
                    return "single_point"
        if not self.ensembles:
            raise ValueError("No ensembles and no point_type in Header")
        return self.ensembles[0].inferred_mode


def _attr_to_str(val: Any) -> str:
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    if isinstance(val, str):
        return val
    if hasattr(val, "decode"):
        return val.decode("utf-8", errors="replace")  # type: ignore[no-any-return]
    return str(val)


def n_regions_from_regions(regions: np.ndarray) -> int:
    r = regions.shape
    if len(r) == 2 and r[1] == 3:
        return int(r[0])
    if len(r) == 1:
        n = int(r[0])
        if n % 3 != 0:
            raise ValueError("regions flat length is not a multiple of 3")
        return n // 3
    raise ValueError(f"Unexpected regions shape {r}")
