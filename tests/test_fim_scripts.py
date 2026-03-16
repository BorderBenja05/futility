import numpy as np
import pytest
import os
import sys
import matplotlib
matplotlib.use('Agg')  # non-interactive backend for tests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fim_scripts.image_analysis import chunk_array, analyze_poisson_noise
from fim_scripts.get_sources import (
    read_txt_file,
    get_indexes_above_threshold,
    get_indexes_of_stars,
    get_indexes_of_all_stars,
)
from fim_scripts.plotting import plotter
from fim_scripts.filefinder import filefinder


# ---------------------------------------------------------------------------
# chunk_array
# ---------------------------------------------------------------------------

def test_chunk_array_output_shape():
    data = np.random.rand(120, 120)
    median, medians, means, stds = chunk_array(data, chunk_size=30)
    # 120 // 30 = 4, so shape = (4+1, 4+1)
    assert medians.shape == (5, 5)
    assert means.shape == (5, 5)
    assert stds.shape == (5, 5)


def test_chunk_array_uniform_data():
    # Use 63x63 so chunks aren't exactly divisible, avoiding empty boundary chunks
    data = np.full((63, 63), 42.0)
    median, medians, means, stds = chunk_array(data, chunk_size=30)
    # All non-NaN cells should equal 42.0
    assert np.allclose(means[~np.isnan(means)], 42.0)
    assert np.allclose(medians[~np.isnan(medians)], 42.0)
    assert np.allclose(stds[~np.isnan(stds)], 0.0)
    assert median == 42.0


def test_chunk_array_non_divisible_size():
    data = np.random.rand(100, 100)
    median, medians, means, stds = chunk_array(data, chunk_size=30)
    # 100 // 30 = 3, shape = (3+1, 3+1) = (4,4)
    assert medians.shape == (4, 4)


# ---------------------------------------------------------------------------
# get_sources (fim_scripts version)
# ---------------------------------------------------------------------------

def make_catalog(tmp_path, rows):
    """Build a minimal 8-line-header catalog file."""
    header = "\n".join(f"#   {i+1} col{i}" for i in range(8))
    lines = [header]
    for row in rows:
        lines.append("  " + "   ".join(str(v) for v in row))
    p = tmp_path / "test.cat"
    p.write_text("\n".join(lines) + "\n")
    return str(p)


def test_fim_read_txt_file(tmp_path):
    rows = [[1, 0.005, 500.0, 400.0, 20.0, 3.0, 1.1]]
    cat = make_catalog(tmp_path, rows)
    data = read_txt_file(cat)
    assert len(data) == 1
    assert data[0][0] == 1


def test_fim_get_indexes_of_stars_no_duplicates():
    # Confirm only one definition of get_indexes_of_stars exists (duplicate removed)
    data = [
        [1, 0.005, 500.0, 500.0, 10.0, 3.0, 1.1],
        [2, 0.010, 500.0, 500.0, 10.0, 3.0, 1.0],
    ]
    result = get_indexes_of_stars(data)
    assert result == [0]


def test_fim_analyze_sources_one_entry_per_source(tmp_path, monkeypatch):
    """analyze_sources should append exactly one entry per source row (loop bug fix)."""
    # Build a catalog with 3 star-like sources
    rows = [
        [1, 0.005, 500.0, 400.0, 20.0, 3.0, 1.1],
        [2, 0.004, 600.0, 300.0, 19.0, 2.5, 1.0],
        [3, 0.006, 700.0, 200.0, 21.0, 4.0, 1.2],
    ]
    cat_path = make_catalog(tmp_path, rows)

    # Monkey-patch os.system so SExtractor is not called
    import fim_scripts.get_sources as gs
    monkeypatch.setattr(gs.os, 'system', lambda cmd: 0)
    monkeypatch.setattr(gs.os.path, 'exists', lambda p: True)

    # Patch read_txt_file to return our rows directly
    monkeypatch.setattr(gs, 'read_txt_file', lambda p: rows)

    # Patch CAT_DIR
    monkeypatch.setattr(gs, 'CAT_DIR', tmp_path)

    x, y, fwhms, spreads, mags, elongations = gs.analyze_sources(
        str(tmp_path / "dummy.fits"), chunksize=60
    )

    # 3 sources → exactly 3 entries each (inner loop bug would give 7 entries per source)
    assert len(x) == 3
    assert len(y) == 3
    assert len(fwhms) == 3
    assert len(spreads) == 3
    assert len(mags) == 3
    assert len(elongations) == 3


# ---------------------------------------------------------------------------
# plotter
# ---------------------------------------------------------------------------

def test_plotter_creates_output_file(tmp_path):
    output_dir = str(tmp_path / "plots")
    plot_args = {
        'infile': 'telescope_test_image.fits',
        'chunks': False,
        'elev': 30,
        'azim': 45,
        'output_dir': output_dir,
        'chunkwidth': 5,
        'chunkheight': 4,
        'ortho': False,
    }
    n = 10
    data_stats = {
        'medians': None,
        'means': None,
        'stds': None,
        'fwhms': list(np.random.uniform(1, 5, n)),
        'spreads': list(np.random.uniform(0, 0.01, n)),
        'mags': list(np.random.uniform(15, 25, n)),
        'x': list(np.random.randint(100, 9000, n)),
        'y': list(np.random.randint(100, 6000, n)),
        'elongations': list(np.random.uniform(1, 2, n)),
    }
    result = plotter(plot_args, data_stats)
    assert result is True
    assert os.path.exists(output_dir)
    png_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
    assert len(png_files) >= 1


def test_plotter_with_chunks(tmp_path):
    output_dir = str(tmp_path / "plots_chunks")
    n_chunks_w, n_chunks_h = 3, 2
    shape = (n_chunks_h + 1, n_chunks_w + 1)
    plot_args = {
        'infile': 'telescope_test_image.fits',
        'chunks': True,
        'elev': 30,
        'azim': 45,
        'output_dir': output_dir,
        'chunkwidth': n_chunks_w,
        'chunkheight': n_chunks_h,
        'ortho': False,
    }
    n = 5
    data_stats = {
        'medians': np.random.uniform(1000, 5000, shape),
        'means': np.random.uniform(1000, 5000, shape),
        'stds': np.random.uniform(10, 100, shape),
        'fwhms': list(np.random.uniform(1, 5, n)),
        'spreads': list(np.random.uniform(0, 0.01, n)),
        'mags': list(np.random.uniform(15, 25, n)),
        'x': list(np.random.randint(100, 9000, n)),
        'y': list(np.random.randint(100, 6000, n)),
        'elongations': list(np.random.uniform(1, 2, n)),
    }
    result = plotter(plot_args, data_stats)
    assert result is True


# ---------------------------------------------------------------------------
# filefinder
# ---------------------------------------------------------------------------

def test_filefinder_finds_fits_files(tmp_path, monkeypatch):
    import fim_scripts.filefinder as ff
    # Create a fake .fits file in a temp dir
    fits_file = tmp_path / "test_image.fits"
    fits_file.write_bytes(b"")

    monkeypatch.setattr(ff, 'FUTILITY_DIR', str(tmp_path))

    matches = ff.filefinder("test_image")
    assert matches is not None
    assert any("test_image" in m for m in matches)


def test_filefinder_returns_none_on_too_many(tmp_path, monkeypatch):
    import fim_scripts.filefinder as ff
    for i in range(12):
        (tmp_path / f"abc_{i}.fits").write_bytes(b"")

    monkeypatch.setattr(ff, 'FUTILITY_DIR', str(tmp_path))
    result = ff.filefinder("abc")
    assert result is None
