# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Install:**
```bash
pip install .
# or: pip install -e .  (editable/dev install)
```

**Run tests:**
```bash
python -m pytest tests/ -v
# Single test file:
python -m pytest tests/test_fim_scripts.py -v
```

**Build package:**
```bash
python -m build
```

**Run the CLI tool:**
```bash
fim [options]
# Show path to default config:
fim -configpath
```

## Architecture

This is a Python astronomy utility package (`futility`) for processing and analyzing FITS astronomical image files.

### CLI Entry Point
`fim_scripts/fim.py` — The `fim` console script entry point. Parses args (elevation/azimuth angles, output path, chunking options) and reads config from `default.cfg` (ConfigParser format).

### Core Modules

**`fits_noise_management.py`** — Primary noise analysis engine. Chunks FITS images and computes statistics (means, medians, standard deviations), then generates 3D matplotlib scatter plots saved to `plots/`.

**`fim_scripts/image_analysis.py`** and **`image_analysis.py`** — Analysis wrappers around the noise management core.

**`get_sources.py`** / **`fim_scripts/get_sources.py`** — Wraps the external `SExtractor` tool (`sex`/`source-extractor` command must be installed separately) to detect astronomical sources. Outputs `.cat` catalog files and filters sources by spread, size, and position thresholds to separate stars from galaxies. Returns FWHM, magnitude, elongation data.

**`gaussian.py`** — Synthetic Gaussian star injection for testing/calibration.

**`difference.py`** — KDTree-based object matching between reference and science images.

**`rotation_finder.py`** / **`drift_calculator.py`** — Camera rotation and drift detection utilities.

**`unpack_folder.py`** — Unpacks compressed FITS files (`.fz` format) using the external `funpack` tool.

### Data Flow
1. Input: FITS files (raw astronomical images, optionally compressed `.fz`)
2. Unpack: `funpack` extracts to `funpacked_fits/`
3. Source extraction: SExtractor produces `.cat` catalogs
4. Analysis: Chunked noise statistics computed over image regions
5. Output: PNG plots in `plots/`, matched source catalogs

### External Dependencies
- **SExtractor** (`sex` or `source-extractor`) — must be installed on the system
- **funpack** — for decompressing `.fz` FITS files
- Python: `numpy`, `matplotlib`, `astropy`, `scikit-learn` (for KDTree)

### Duplicate Files
Several modules exist at both the root level and inside `fim_scripts/` (e.g., `get_sources.py`, `image_analysis.py`). The `fim_scripts/` versions are packaged and used by the CLI; the root-level versions are standalone scripts.
