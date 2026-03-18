# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Install:**
```bash
pip install -e .  # editable/dev install (recommended for development)
pip install .     # standard install
```

**Run tests:**
```bash
python -m pytest tests/ -v
python -m pytest tests/test_fim_scripts.py -v          # single test file
python -m pytest tests/test_fim_scripts.py::test_name -v  # single test
```

**Build package:**
```bash
python -m build
```

**Run the CLI tool:**
```bash
fim [infile]              # analyze a FITS file
fim -v ELEV AZIM          # set 3D plot viewing angles
fim -o PATH               # set output directory (default: plots/)
fim -chunks               # enable chunked averaging
fim -ortho                # orthographic projection
fim -configpath            # show path to default.cfg
```

## Architecture

Python astronomy utility package (`futility`, v0.3.4) for processing and analyzing FITS image files. Entry point: `fim` console script → `fim_scripts.fim:main()`.

### Data Flow
1. **Input** — Raw FITS files (optionally `.fz` compressed)
2. **Unpack** — `unpack_folder.py` calls external `funpack` → output in `funpacked_fits/`
3. **Source extraction** — `get_sources.py` wraps external SExtractor → `.cat` catalogs in `fim_scripts/fim_data/catalogs/`
4. **Analysis** — `image_analysis.py` chunks images (default 60px), computes per-chunk means/medians/stddevs
5. **Visualization** — `plotting.py` generates 3D matplotlib scatter plots → `plots/`
6. **Matching** — `difference.py` uses KDTree to match sources between reference and science images

### Key Modules

| Module | Role |
|--------|------|
| `fim_scripts/fim.py` | CLI entry point — arg parsing, config loading (`default.cfg`) |
| `fim_scripts/filefinder.py` | Recursive FITS file discovery with interactive fallback |
| `fim_scripts/image_analysis.py` | Chunked Poisson noise analysis (packaged version) |
| `fim_scripts/get_sources.py` | SExtractor wrapper — star/galaxy separation by spread threshold |
| `fim_scripts/plotting.py` | 3D scatter plot generation (uses `Agg` backend in tests, `ion()` in CLI) |
| `fits_noise_management.py` | Primary noise analysis engine (standalone version) |
| `gaussian.py` | Synthetic Gaussian star injection for calibration |
| `difference.py` | KDTree-based source matching (radius=4 default) |
| `flats_noise.py` | Flat-field noise analysis |
| `gym_teacher.py` | Gaussian injection with XML logging |

### Duplicate Modules
`get_sources.py` and `image_analysis.py` exist at both root and `fim_scripts/`. The `fim_scripts/` versions are the packaged ones used by the CLI; root versions are standalone scripts. When modifying functionality, update the `fim_scripts/` version (it's what gets installed).

### External System Dependencies
- **SExtractor** (`sex` or `source-extractor` command) — required for source detection
- **funpack** — required for `.fz` FITS decompression
- SExtractor config files live in `fim_scripts/fim_data/` (`default.sex`, `default.conv`, `starfinder.param`, `default.psf`)

### Source Detection Thresholds
Star/galaxy filtering uses position bounds X ∈ [80, 9495], Y ∈ [80, 6307] and spread-based classification. These values are hardcoded in `get_sources.py`.

### Config
`default.cfg` (ConfigParser format) at both root and `fim_scripts/` — stores default `elev`, `azim`, `outpath`, and `inpath` values. The `fim_scripts/` copy is the one included in the installed package.

### Testing Notes
- Tests monkeypatch SExtractor calls and file I/O (no external tools needed to run tests)
- Tests use matplotlib `Agg` backend for headless rendering
- Package uses `setup.py` (no pyproject.toml) — `python_requires >= 3.6`
