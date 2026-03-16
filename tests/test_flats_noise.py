import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flats_noise import analyze_poisson_noise, noise_maker1


def make_fits_file(tmp_path, data=None):
    from astropy.io import fits
    if data is None:
        data = np.random.randint(1000, 5000, size=(120, 120), dtype=np.uint16)
    path = tmp_path / "test.fits"
    hdu = fits.PrimaryHDU(data)
    hdu.writeto(str(path), overwrite=True)
    return str(path)


def test_analyze_poisson_noise_returns_correct_shape():
    data = np.random.randint(1000, 5000, size=(120, 120)).astype(np.float32)
    medians, stds, median, shape = analyze_poisson_noise(data, chunk_size=30)
    assert medians.shape == stds.shape
    assert shape == (120, 120)
    assert isinstance(median, (float, np.floating))


def test_analyze_poisson_noise_just_return_denoise():
    data = np.random.randint(1000, 5000, size=(60, 60)).astype(np.float32)
    result = analyze_poisson_noise(data, chunk_size=30, just_return_denoise=True)
    assert result.shape == (60, 60)


def test_analyze_poisson_noise_chunk_count():
    data = np.ones((90, 90))
    medians, stds, median, shape = analyze_poisson_noise(data, chunk_size=30)
    # 90 // 30 = 3, so shape should be (3+1, 3+1) = (4, 4)
    assert medians.shape == (4, 4)
    assert stds.shape == (4, 4)


def test_noise_maker1(tmp_path):
    fits_path = make_fits_file(tmp_path)
    result = noise_maker1(fits_path)
    assert result.dtype == np.uint16
    assert result.min() >= 1
    assert result.max() <= 65535


def test_noise_maker1_preserves_shape(tmp_path):
    from astropy.io import fits
    data = np.random.randint(1000, 5000, size=(100, 80), dtype=np.uint16)
    path = tmp_path / "test.fits"
    fits.PrimaryHDU(data).writeto(str(path), overwrite=True)
    result = noise_maker1(str(path))
    assert result.shape == (100, 80)
