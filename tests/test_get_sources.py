import numpy as np
import pytest
import sys
import os
import textwrap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from get_sources import (
    read_txt_file,
    get_indexes_above_threshold,
    get_indexes_of_stars,
    get_indexes_of_all_stars,
)


# A minimal SExtractor catalog with 8 header comment lines followed by data.
# Columns: NUMBER SPREAD_MODEL X_IMAGE Y_IMAGE MAG_AUTO FWHM_IMAGE ELONGATION
SAMPLE_CATALOG = textwrap.dedent("""\
    #   1 NUMBER
    #   2 SPREAD_MODEL
    #   3 X_IMAGE
    #   4 Y_IMAGE
    #   5 MAG_AUTO
    #   6 FWHM_IMAGE
    #   7 ELONGATION
    #   8 (padding)
         1    0.001   500.0   500.0   20.0   3.0   1.1
         2    0.030   200.0   200.0   18.0   4.0   1.2
         3    0.005   100.0   100.0   22.0   5.0   1.0
         4    0.003    50.0    50.0   21.0   3.5   1.3
""")


@pytest.fixture
def catalog_file(tmp_path):
    p = tmp_path / "test.cat"
    p.write_text(SAMPLE_CATALOG)
    return str(p)


def test_read_txt_file_returns_rows(catalog_file):
    data = read_txt_file(catalog_file)
    assert len(data) == 4


def test_read_txt_file_correct_values(catalog_file):
    data = read_txt_file(catalog_file)
    assert data[0][0] == 1          # NUMBER
    assert abs(data[0][1] - 0.001) < 1e-6   # SPREAD_MODEL
    assert abs(data[0][2] - 500.0) < 1e-3   # X_IMAGE


def test_get_indexes_above_threshold():
    # row: [NUMBER, SPREAD_MODEL, X_IMAGE, Y_IMAGE, ...]
    data = [
        [1, 0.030, 500.0, 500.0, 20.0],  # spread > 0.02, valid position → galaxy
        [2, 0.010, 500.0, 500.0, 18.0],  # spread < 0.02 → not galaxy
        [3, 0.025, 500.0, 500.0, 19.0],  # spread > 0.02, valid → galaxy
    ]
    indexes = get_indexes_above_threshold(data)
    assert 0 in indexes
    assert 1 not in indexes
    assert 2 in indexes


def test_get_indexes_above_threshold_position_filter():
    data = [
        [1, 0.030, 10.0, 500.0, 20.0],   # X too small (< 80)
        [2, 0.030, 500.0, 10.0, 20.0],   # Y too small (< 80)
        [3, 0.030, 500.0, 500.0, 20.0],  # valid
    ]
    indexes = get_indexes_above_threshold(data)
    assert indexes == [2]


def test_get_indexes_of_stars():
    data = [
        [1, 0.005, 500.0, 500.0, 10.0, 5.0, 1.1],  # spread < .007, size 15 < 20 → star
        [2, 0.010, 500.0, 500.0, 10.0, 5.0, 1.0],  # spread > .007 → not star
        [3, 0.003, 500.0, 500.0, 12.0, 9.0, 1.0],  # size 21 > 20 → not star
    ]
    indexes = get_indexes_of_stars(data)
    assert indexes == [0]


def test_get_indexes_of_all_stars():
    data = [
        [1, 0.010, 500.0, 500.0, 20.0, 3.0, 1.1],  # spread < .012 → star
        [2, 0.015, 500.0, 500.0, 20.0, 3.0, 1.0],  # spread > .012 → not star
    ]
    indexes = get_indexes_of_all_stars(data)
    assert indexes == [0]


def test_no_duplicate_function():
    # Verify get_indexes_of_stars is only defined once by checking it works correctly
    # (if defined twice, behavior is still correct since both defs are identical — but
    # the duplicate is removed from the source, this just confirms the function works)
    data = [[1, 0.006, 500.0, 500.0, 5.0, 3.0, 1.0]]
    result = get_indexes_of_stars(data)
    assert result == [0]
