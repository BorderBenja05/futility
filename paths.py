from pathlib import Path
import os



FUTILITY_DIR = Path(__file__).parent.absolute()
OUTSIDE_DIR = FUTILITY_DIR.parent.absolute()
FUNPACKED_FITS = FUTILITY_DIR.joinpath('funpacked_fits')
INJECTED_FITS = FUTILITY_DIR.joinpath('injected_fits')
CAT_DIR = FUNPACKED_FITS.joinpath('catalogs')
FIM_DATA_DIR = FUTILITY_DIR.joinpath('fim_scripts', 'fim_data')

if not os.path.exists(CAT_DIR):
    os.mkdir(CAT_DIR)
if not os.path.exists(INJECTED_FITS):
    os.mkdir(INJECTED_FITS)


