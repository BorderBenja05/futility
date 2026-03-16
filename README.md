# futility

A Python astronomy utility package for processing and analyzing FITS astronomical image files. Focuses on noise analysis, source detection, and camera calibration.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Tool: `fim`](#cli-tool-fim)
- [Configuration](#configuration)
- [Modules](#modules)
  - [Noise Analysis](#noise-analysis)
  - [Source Detection](#source-detection)
  - [Visualization](#visualization)
  - [File Handling](#file-handling)
  - [Synthetic Star Injection](#synthetic-star-injection)
  - [Source Matching](#source-matching)
  - [Camera Calibration](#camera-calibration)
- [Data Flow](#data-flow)
- [External Dependencies](#external-dependencies)
- [Running Tests](#running-tests)

---

## Installation

```bash
pip install .
# or for development (editable install):
pip install -e .
```

**Python 3.6+ required.** Python dependencies installed automatically: `numpy`, `matplotlib`, `astropy`, `scikit-learn`.

---

## Quick Start

```bash
# Analyze a FITS file with default settings
fim /path/to/image.fits

# Include chunk statistics (means, medians, stds across image regions)
fim -chunks /path/to/image.fits

# Set custom viewing angles for 3D plots
fim -v 20 60 /path/to/image.fits

# Write plots to a specific directory
fim -o /tmp/results /path/to/image.fits

# All together
fim -chunks -v 30 45 -o ./results /path/to/image.fits
```

---

## CLI Tool: `fim`

```
fim [options] [INFILE]
```

| Argument | Description |
|---|---|
| `INFILE` | Path to input FITS file (optional — falls back to `default.cfg`) |
| `-v ELEV AZIM` | Set elevation and azimuth angles for 3D plots (two integers) |
| `-ortho` | Use orthographic projection in 3D plots |
| `-chunks` | Enable chunked averaging: compute and plot per-region statistics |
| `-o OUTPATH` | Output directory for saved plots (default: `plots/`) |
| `-configpath` | Print path to the active `default.cfg` file and exit |

If `INFILE` is not given, the tool reads `inpath` from `default.cfg`. If the path doesn't exist, `fim` will search the futility directory recursively for `.fits` files and prompt you to select one.

---

## Configuration

`fim` reads defaults from `default.cfg` (INI format). Run `fim -configpath` to find where it lives.

```ini
[DEFAULT]
elev = 30
azim = 45
outpath = plots
inpath = /path/to/your/image.fits
```

CLI arguments always override config values.

---

## Modules

### Noise Analysis

#### `fim_scripts/image_analysis.py` — used by the CLI

```python
from fim_scripts.image_analysis import analyze_poisson_noise

analyze_poisson_noise(
    infile,       # Path to FITS file
    elev,         # Elevation angle for 3D plot
    azim,         # Azimuth angle for 3D plot
    chunks,       # bool — compute chunk statistics
    ortho,        # bool — orthographic projection
    chunk_size=60,
    plots=True,
    output_dir='plots'
)
```

Loads the FITS image, auto-detects the HDU structure (1-HDU or 6-HDU files), computes per-chunk statistics if requested, runs source detection, and calls `plotter()` to save the results.

#### `flats_noise.py` — programmatic use

```python
from flats_noise import analyze_poisson_noise, noise_maker1

# Chunk an image array and return statistics
medians, stds, overall_median, shape = analyze_poisson_noise(data, chunk_size=30)

# Return a denoised image only
denoised = analyze_poisson_noise(data, chunk_size=30, just_return_denoise=True)

# Generate a noisy copy of a FITS file (for testing)
noisy_array = noise_maker1('/path/to/flat.fits')
```

---

### Source Detection

Wraps SExtractor to detect stars and galaxies. **SExtractor must be installed** (`sex` or `source-extractor` on your PATH).

```python
from fim_scripts.get_sources import analyze_sources

x, y, fwhms, spreads, mags, elongations = analyze_sources(
    infile,               # Path to FITS file
    chunksize=60,
    chunked_shape=None    # Pass chunk grid shape to align coordinates
)
```

Returns lists of per-star properties for all sources that pass the star filter (SExtractor spread < 0.012, position within sensor bounds).

**Lower-level helpers:**

```python
from fim_scripts.get_sources import (
    read_txt_file,              # Parse a .cat SExtractor catalog file
    get_indexes_of_all_stars,   # Filter by spread < 0.012
    get_indexes_of_stars,       # Stricter filter: spread < 0.007, size < 20
    get_indexes_above_threshold # Galaxy filter: spread > 0.02
)
```

SExtractor output catalogs are cached as `<name>.analysis.cat` so repeated calls skip re-running extraction.

---

### Visualization

```python
from fim_scripts.plotting import plotter

plotter(args, data_stats)
```

**`args` dict:**

```python
args = {
    'infile':      '/path/to/image.fits',
    'chunks':      True,           # Whether to plot chunk-level stats
    'elev':        40,             # 3D plot elevation
    'azim':        40,             # 3D plot azimuth
    'output_dir':  'plots',
    'chunkwidth':  160,            # Number of chunks along x
    'chunkheight': 107,            # Number of chunks along y
    'ortho':       False,
}
```

**`data_stats` dict:**

```python
data_stats = {
    'medians':     ndarray,   # 2D array of per-chunk medians (or None)
    'means':       ndarray,   # 2D array of per-chunk means (or None)
    'stds':        ndarray,   # 2D array of per-chunk std devs (or None)
    'fwhms':       list,      # FWHM for each detected star
    'spreads':     list,      # Spread parameter per star
    'mags':        list,      # Auto magnitude per star
    'x':           list,      # X pixel coordinates
    'y':           list,      # Y pixel coordinates
    'elongations': list,      # Elongation (major/minor axis ratio)
}
```

**Output files** saved to `output_dir`:

| File | Contents | Requires `chunks` |
|---|---|---|
| `{name}_3d_info.png` | 3D scatter of medians and means vs position | yes |
| `{name}_ms_vs_stds_info.png` | 2D scatter of means & medians vs std devs | yes |
| `{name}_3d_star_info.png` | 4-panel: FWHM, spread, magnitude, elongation | no |

---

### File Handling

#### Decompressing `.fz` FITS files

FITS files compressed with `fpack` have a `.fz` extension. Use `unpack_folder.py` to decompress them. **`funpack` must be installed.**

```bash
# Decompress in-place (renames .fits → .fz, runs funpack, renames back)
python unpack_folder.py /path/to/folder

# Decompress and move results to a different directory
python unpack_folder.py /path/to/folder /output/dir

# Interactive: will prompt for folder path
python unpack_folder.py
```

Or call programmatically:

```python
from unpack_folder import rename_files, move_files

rename_files('/path/to/folder')
move_files('/path/to/folder', '/output/dir')
```

---

### Synthetic Star Injection

Inject synthetic Gaussian stars into FITS images for testing and calibration.

```python
from gaussian import insert_gaussians, inject_star, gaussian

# Inject stars at specific galaxy positions
output_file, injections = insert_gaussians(
    f_in='original.fits',      # Input FITS file
    f_out='./injected/',       # Output directory
    siga=0.5,                  # Min sigma for injected PSF
    sigb=1.5,                  # Max sigma for injected PSF
    gals=[[100, 200], [300, 400]],  # List of [x, y] positions
    iter=0                     # Iteration index (appended to filename)
)
# Creates: ./injected/original.injected0.fits
# injections: [[x, y, sigma, amplitude], ...]

# Inject a single star into an array
modified_data, injections = inject_star(
    dat,           # uint16 image array
    galx=500,      # Center x
    galy=300,      # Center y
    siga=0.5,      # Min sigma
    sigb=1.5,      # Max sigma
    injections=[]  # List to append injection record to
)

# Generate a 2D Gaussian kernel
kernel = gaussian(xlength=10, ylength=10, sigma=1.2)
# Returns ndarray of shape (ylength, xlength), values in [0, 1]
```

---

### Source Matching

Compare detections between two images (e.g. reference vs science frame) to find new sources.

```python
from difference import check_for_matches, read_cat_file

reference = read_cat_file('reference.cat')
science   = read_cat_file('science.cat')

# Returns rows in `science` with no match in `reference` within 4 pixels
new_sources = check_for_matches(reference, science)
```

Catalog rows are expected in SExtractor format: `[id, spread, x, y, ...]`.

---

### Camera Calibration

#### Pixel scale and rotation angle

Requires `sewpy` (`pip install sewpy`) and two reference sources with known sky coordinates.

```python
from rotation_finder import get_cam_angle, get_pixelscale

# Reference source format: [[RA_h, RA_m, RA_s], [Dec_d, Dec_m, Dec_s]]
source1 = [[19, 30, 43.3], [27, 57, 34.7]]
source2 = [[19, 30, 45.4], [27, 57, 55.0]]

# Camera rotation angle (degrees)
angle = get_cam_angle('image.fits', source1, source2)

# Rotation + pixel scale (arcsec/px)
angle, pixscale = get_cam_angle('image.fits', source1, source2, scale=True)

# Pixel scale only
pixscale = get_pixelscale('image.fits', source1, source2)
```

#### Drift velocity over a series of frames

```python
from drift_calculator import drift_calculator

Vxs, Vys, angle, pixscale = drift_calculator(
    inpath='/path/to/image_series/',  # Directory of .fits files
    source1=source1,
    source2=source2
)
# Vxs, Vys: lists of velocities in arcsec/s for each frame pair
# angle:    average camera rotation across all frames
# pixscale: average pixel scale across all frames
```

---

## Data Flow

```
Input FITS file (.fits or .fz)
       │
       ▼ (if .fz)
 unpack_folder.py  →  funpacked_fits/  (uses funpack)
       │
       ▼
   fim CLI  →  filefinder.py  (finds file, resolves path)
       │
       ▼
 image_analysis.py  (loads FITS, auto-detects HDU)
       │
       ├── chunk_array()     →  medians / means / stds per 60×60 region
       │
       └── get_sources.py    →  SExtractor  →  .analysis.cat
                                    │
                                    ▼
                             filter stars (spread < 0.012)
                             x, y, FWHM, spread, mag, elongation
       │
       ▼
  plotting.py  →  PNG files in output_dir/
```

---

## External Dependencies

These tools must be installed on your system separately from the Python package:

| Tool | Purpose | Install |
|---|---|---|
| `source-extractor` | Astronomical source detection | `apt install source-extractor` or see [SExtractor docs](https://www.astromatic.net/software/sextractor/) |
| `funpack` | Decompress `.fz` FITS files | `apt install libcfitsio-bin` |

SExtractor configuration files (`default.sex`, `default.conv`, `analysis.param`, etc.) are bundled in `fim_scripts/fim_data/`.

---

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_fim_scripts.py -v
python -m pytest tests/test_gaussian.py -v
python -m pytest tests/test_flats_noise.py -v
```

Tests cover: chunk analysis, source filtering, plot generation, file discovery, Gaussian injection, and noise generation.
