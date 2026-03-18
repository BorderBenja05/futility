# futility

A Python toolkit for unpacking, analyzing, and visualizing FITS astronomical image files. Includes a CLI tool (`fim`) for interactive noise analysis and 3D plotting, plus standalone utilities for source extraction, synthetic star injection, image differencing, and camera rotation/drift detection.

## Installation

### Requirements

- Python >= 3.6
- **SExtractor** (`source-extractor` or `sex` command) -- must be installed separately on your system for source detection features
- **funpack** -- must be installed separately for decompressing `.fz` FITS files

### Install from source

```bash
git clone https://github.com/borderbenja05/futility.git
cd futility
pip install .
```

For development (editable install):

```bash
pip install -e .
```

Python dependencies (`numpy`, `matplotlib`, `astropy`, `scikit-learn`) are installed automatically.

## CLI Usage: `fim`

After installation, the `fim` command is available on your PATH. It analyzes a FITS file, runs source extraction via SExtractor, and generates 3D scatter plots of stellar properties (FWHM, spread, magnitude, elongation).

### Basic usage

```bash
# Analyze a FITS file with default settings
fim /path/to/image.fits

# If no file is provided, fim reads the input path from default.cfg
fim
```

If the file isn't found at the given path, `fim` will search recursively through the project directory and prompt you interactively to select a match.

### Options

```
fim [options] [infile]

positional arguments:
  infile               Path to a FITS file (optional; falls back to default.cfg)

options:
  -v ELEV AZIM         Set the 3D plot viewing angle (elevation and azimuth in degrees)
  -o PATH              Output directory for plot PNGs (default: plots/)
  -chunks              Enable chunked averaging -- computes per-chunk means, medians,
                       and standard deviations across the image and generates additional
                       noise statistic plots
  -ortho               Use orthographic projection instead of perspective for 3D plots
  -configpath          Print the path to the default.cfg config file and exit
```

### Examples

```bash
# Analyze with custom viewing angle
fim -v 60 120 /path/to/image.fits

# Enable chunked noise statistics and save to a custom directory
fim -chunks -o results/ /path/to/image.fits

# Use orthographic projection
fim -ortho -v 45 90 /path/to/image.fits

# Find where the config file is so you can edit defaults
fim -configpath
```

### Configuration

Default values for `elev`, `azim`, `outpath`, and `inpath` are stored in `default.cfg` (INI format):

```ini
[DEFAULT]
elev = 30
azim = 45
outpath = plots
inpath = /path/to/your/default.fits
```

Find this file with `fim -configpath` and edit it to set your own defaults.

### Output plots

All plots are saved as PNGs to the output directory (default: `plots/`).

**Always generated:**
- `{name}_3d_star_info.png` -- Four-panel 3D scatter plot showing FWHM, spread, magnitude, and elongation of detected stars across the image

**With `-chunks` enabled:**
- `{name}_3d_info.png` -- Side-by-side 3D scatter plots of per-chunk medians and means
- `{name}_ms_vs_stds_info.png` -- 2D scatter plot of means/medians vs. standard deviations (Poisson noise diagnostic)

### FITS file handling

The tool automatically selects the correct HDU based on the file structure:
- Single-extension FITS: reads `hdul[0]`
- 6-extension FITS (processed files): reads `hdul[4]`
- Other: prompts you to specify which HDU index to use

## Standalone Modules

These modules can be used independently as scripts or imported into your own code.

### Unpacking compressed FITS files

`unpack_folder.py` decompresses `.fz` files using the external `funpack` tool.

```bash
# Unpack all .fz files in a folder (in place)
python unpack_folder.py /path/to/folder/

# Unpack and move the resulting .fits files to another directory
python unpack_folder.py /path/to/folder/ /path/to/output/
```

From Python:

```python
from unpack_folder import rename_files, move_files

rename_files("/path/to/folder/")         # decompress .fz -> .fits in place
move_files("/path/to/folder/", "/dest/") # move all files to destination
```

### Source extraction

`get_sources.py` wraps SExtractor to detect and classify sources in FITS images. It runs SExtractor if a catalog doesn't already exist, then parses the resulting `.cat` file.

```python
from get_sources import getcenter, getStars, analyze_sources

# Get galaxy-like source positions (spread > 0.02)
galaxies = getcenter("/path/to/image.fits")
# Returns: [[x1, y1], [x2, y2], ...]

# Get star-like source positions (spread < 0.007, size < 20)
stars = getStars("/path/to/image.fits")
# Returns: [[x1, y1], [x2, y2], ...]

# Full analysis -- returns arrays of source properties
x, y, fwhms, spreads, mags, elongations = analyze_sources("/path/to/image.fits")
```

Source classification thresholds:
- **Stars**: `spread < 0.007`, sum of major+minor axes < 20
- **All stars** (relaxed): `spread < 0.012`
- **Galaxies**: `spread > 0.02`
- **Position bounds**: sources outside X [80, 9495] and Y [80, 6307] are excluded (edge filtering)

Catalogs are cached in `fim_scripts/fim_data/catalogs/` -- if a catalog already exists for a given FITS file, SExtractor is not re-run.

### Noise analysis

`flats_noise.py` provides chunked Poisson noise analysis on raw image arrays.

```python
from flats_noise import analyze_poisson_noise, noise_maker1

# Analyze noise from a 2D numpy array (e.g., FITS image data)
medians, stds, median, shape = analyze_poisson_noise(data, chunk_size=30)

# Load a FITS file and return its data clipped to uint16 range [1, 65535]
cleaned_data = noise_maker1("/path/to/image.fits")
```

`fits_noise_management.py` is a higher-level version that combines noise analysis with source extraction and plotting (this is what the `fim` CLI uses internally).

### Synthetic star injection

`gaussian.py` creates 2D Gaussian profiles and injects them into FITS images for testing and calibration.

```python
from gaussian import gaussian, inject_star, insert_gaussians

# Generate a 10x10 Gaussian kernel with sigma=1.2
kernel = gaussian(10, 10, sigma=1.2)

# Inject a single synthetic star near position (galx, galy)
# The star is placed at a random offset (7-40 pixels) from the given position
injections = []
modified_data, injections = inject_star(data, galx=500, galy=500, siga=0.5, sigb=1.3, injections=injections)
# injections contains [x, y, sigma, amplitude] for each injection

# Process an entire file: inject stars near galaxy positions, write new FITS
output_path, injections = insert_gaussians(
    "/path/to/input.fits",
    "/path/to/output/dir/",
    siga=0.5,      # minimum sigma for random star width
    sigb=1.3,      # maximum sigma for random star width
    gals=[[x1,y1], [x2,y2]],  # positions to inject near
    iter=0          # iteration number (appended to filename)
)
```

Injected stars have:
- Random amplitude between 675 and 5000 ADU
- Random sigma between `siga` and `sigb`
- Random positional offset (7-40 pixels) at a random angle from the target position
- Sub-pixel centering jitter for realism

### Training data generation

`gym_teacher.py` automates bulk synthetic star injection for creating ML training datasets. It detects galaxy positions in an image, splits them across multiple output files, injects synthetic stars near those positions, and logs all injection coordinates to `starcoords.xml`.

```python
from gym_teacher import make_trainer

# Generate 8-10 copies of the input image, each with 30-50 injected stars
make_trainer("/path/to/image.fits", "/path/to/output/dir/")
```

The XML log format:

```xml
<filename>
    <injection0>
        <x>4312</x>
        <y>3971</y>
        <sigma>0.83</sigma>
        <amp>2145.0</amp>
    </injection0>
    ...
</filename>
```

### Image differencing

`difference.py` uses a KDTree to match sources between a reference and science image, identifying new objects.

```python
from difference import check_for_matches, find_new_row, read_cat_file

# Read SExtractor .cat catalog files
ref_data = read_cat_file("reference.cat")
sci_data = read_cat_file("science.cat")

# Find sources in the science image with no match within 4 pixels in the reference
new_sources = check_for_matches(ref_data, sci_data)
# Returns: list of [x, y] positions of unmatched sources

# Alternative: find new rows by exact coordinate comparison (rounded to integers)
new_rows = find_new_row(ref_data, sci_data)
```

### Camera rotation finder

`rotation_finder.py` determines camera rotation angle and pixel scale by comparing known celestial coordinates of two sources to their pixel positions. Requires the optional `sewpy` package.

```python
from rotation_finder import get_cam_angle, get_pixelscale

# Source coordinates as [[RA_h, RA_m, RA_s], [Dec_d, Dec_m, Dec_s]]
source1 = [[19, 30, 43.288], [27, 57, 34.73]]
source2 = [[19, 30, 45.396], [27, 57, 54.989]]

# Get camera rotation angle (degrees)
angle = get_cam_angle("/path/to/image.fits", source1, source2)

# Also get pixel scale (arcsec/pixel)
angle, pixscale = get_cam_angle("/path/to/image.fits", source1, source2, scale=True)

# Also get the source table
angle, pixscale, table = get_cam_angle("/path/to/image.fits", source1, source2, scale=True, pos=True)

# Get pixel scale directly
pixscale = get_pixelscale("/path/to/image.fits", source1, source2)
```

### Drift calculator

`drift_calculator.py` measures tracking drift across a sequence of FITS exposures in a directory. It reads `DATE-OBS` headers, sorts by time, and computes per-frame drift velocities in arcsec/second.

```python
from drift_calculator import drift_calculator

source1 = [[19, 30, 43.288], [27, 57, 34.73]]
source2 = [[19, 30, 45.396], [27, 57, 54.989]]

# Analyze all .fits files in a directory
Vxs, Vys, avg_angle, avg_pixscale = drift_calculator("/path/to/exposures/", source1, source2)
# Vxs, Vys: drift velocities (arcsec/sec) for each frame transition
# avg_angle: average camera rotation angle (degrees)
# avg_pixscale: average pixel scale (arcsec/pixel)
```

## Project Structure

```
futility/
├── fim_scripts/              # Installed package (used by `fim` CLI)
│   ├── fim.py                # CLI entry point
│   ├── filefinder.py         # Recursive FITS file discovery
│   ├── image_analysis.py     # Chunked noise analysis + source analysis
│   ├── get_sources.py        # SExtractor wrapper (packaged)
│   ├── plotting.py           # 3D matplotlib visualization
│   ├── paths.py              # Path constants
│   ├── default.cfg           # Default configuration
│   └── fim_data/             # SExtractor config files and catalogs
│       ├── default.conv      # Convolution filter
│       ├── default.psf       # PSF model
│       ├── default.param     # Starfinder output parameters
│       └── analysis.param    # Analysis output parameters
├── fits_noise_management.py  # Standalone noise analysis + plotting
├── flats_noise.py            # Low-level chunked noise computation
├── get_sources.py            # Standalone SExtractor wrapper
├── gaussian.py               # Synthetic star injection
├── gym_teacher.py            # Bulk training data generator
├── difference.py             # KDTree source matching
├── rotation_finder.py        # Camera rotation detection (requires sewpy)
├── drift_calculator.py       # Tracking drift measurement
├── unpack_folder.py          # .fz decompression utility
├── tests/                    # Unit tests (pytest)
├── plots/                    # Generated plot output
├── funpacked_fits/           # Unpacked FITS files
└── injected_fits/            # Synthetic star output
```

## Running Tests

```bash
python -m pytest tests/ -v
```

Tests do not require SExtractor or funpack to be installed -- external tool calls are monkeypatched.

## License

MIT
