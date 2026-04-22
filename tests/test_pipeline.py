from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np
import pytest

from pc2bs.convert import pointcloud_to_ballstick
from pc2bs.read import read_sw
from pc2bs.write import write_sw

DATA = Path(__file__).resolve().parents[2] / "data"
POINTCLOUD = DATA / "pointcloud" / "multiple-traces-multiple-genomic-locations.sw"


@pytest.mark.skipif(not POINTCLOUD.is_file(), reason="sample .sw not present")
def test_read_write_roundtrip_pointcloud(tmp_path: Path) -> None:
    doc = read_sw(POINTCLOUD)
    out = tmp_path / "rw.sw"
    write_sw(doc, out)
    again = read_sw(out)
    assert again.effective_point_mode() == "multi_point"
    assert np.allclose(doc.ensembles[0].traces["t_0"], again.ensembles[0].traces["t_0"], equal_nan=True)
    with h5py.File(out, "r") as f:
        assert "_index" not in f
        assert "_index_offset" not in f.attrs


@pytest.mark.skipif(not POINTCLOUD.is_file(), reason="sample .sw not present")
def test_pointcloud_to_ballstick_cli_path(tmp_path: Path) -> None:
    out = tmp_path / "bs.sw"
    pointcloud_to_ballstick(POINTCLOUD, out)
    doc = read_sw(out)
    assert doc.effective_point_mode() == "single_point"
    assert doc.ensembles[0].traces["t_0"].shape == (9, 3)
    with h5py.File(out, "r") as f:
        assert "_index" in f
        assert {"Header", "PGP1"} <= set(f.keys())


@pytest.mark.skipif(not POINTCLOUD.is_file(), reason="sample .sw not present")
def test_pointcloud_to_ballstick_no_index(tmp_path: Path) -> None:
    out = tmp_path / "bs.sw"
    pointcloud_to_ballstick(POINTCLOUD, out, index=False)
    with h5py.File(out, "r") as f:
        assert "_index" not in f


@pytest.mark.skipif(not POINTCLOUD.is_file(), reason="sample .sw not present")
def test_rejects_ballstick_input(tmp_path: Path) -> None:
    bs = tmp_path / "bs.sw"
    pointcloud_to_ballstick(POINTCLOUD, bs)
    with pytest.raises(ValueError, match="only converts point-cloud"):
        pointcloud_to_ballstick(bs, tmp_path / "out.sw")


@pytest.mark.skipif(not POINTCLOUD.is_file(), reason="sample .sw not present")
def test_ballstick_output_includes_live_contact_map_vertices_bake(tmp_path: Path) -> None:
    out = tmp_path / "bs.sw"
    pointcloud_to_ballstick(POINTCLOUD, out)

    doc = read_sw(out)
    ensemble = doc.ensembles[0]
    trace_names = sorted(ensemble.traces.keys(), key=lambda n: int(n[2:]) if n[2:].isdigit() else n)
    trace_count = len(trace_names)
    trace_length = ensemble.traces[trace_names[0]].shape[0]

    with h5py.File(out, "r") as f:
        assert f["Header"].attrs["live_contact_map_vertices_version"] == 1
        bake = f[ensemble.name]["live_contact_map_vertices"]
        assert bake.shape == (trace_count, trace_length, 3)
        assert bake.dtype == np.float32

        # Bake must match the per-trace datasets exactly (same source data,
        # just restructured; NaN positions preserved).
        baked = bake[...]
        for i, name in enumerate(trace_names):
            t = np.asarray(ensemble.traces[name], dtype=np.float32)
            assert np.array_equal(baked[i], t, equal_nan=True)
