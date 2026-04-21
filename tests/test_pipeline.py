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
