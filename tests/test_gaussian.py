import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gaussian import gaussian, inject_star


def test_gaussian_shape():
    result = gaussian(10, 10, 1.0)
    assert result.shape == (10, 10)


def test_gaussian_peak_near_center():
    result = gaussian(21, 21, 2.0)
    # Peak should be near the center
    peak_idx = np.unravel_index(np.argmax(result), result.shape)
    center = (10, 10)
    assert abs(peak_idx[0] - center[0]) <= 2
    assert abs(peak_idx[1] - center[1]) <= 2


def test_gaussian_values_between_0_and_1():
    result = gaussian(10, 10, 1.5)
    assert result.min() >= 0.0
    assert result.max() <= 1.0 + 1e-10  # allow tiny floating point overshoot


def test_gaussian_non_square():
    # gaussian(xlength, ylength, sigma) uses meshgrid so shape is (ylength, xlength)
    result = gaussian(8, 12, 1.0)
    assert result.shape == (12, 8)


def test_inject_star_modifies_data():
    # Use a large enough array so the random shift (max ~80px) stays in bounds
    dat = np.zeros((300, 300), dtype=np.uint16)
    injections = []
    dat_out, injections_out = inject_star(dat.copy(), 150, 150, 0.5, 1.5, injections)
    assert dat_out.sum() > 0
    assert len(injections_out) == 1


def test_inject_star_records_position():
    dat = np.zeros((300, 300), dtype=np.uint16)
    injections = []
    _, injections_out = inject_star(dat, 150, 150, 0.5, 1.5, injections)
    x, y, sigma, amp = injections_out[0]
    # Sigma and amplitude should be within the requested ranges
    assert 0.5 <= sigma <= 1.5
    assert 675 <= amp <= 5000


def test_inject_star_clips_to_bounds():
    # Injection near the edge should not raise IndexError
    dat = np.zeros((50, 50), dtype=np.uint16)
    injections = []
    dat_out, _ = inject_star(dat.copy(), 2, 2, 0.5, 1.0, injections)
    assert dat_out.shape == (50, 50)
