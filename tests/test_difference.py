import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from difference import check_for_matches, find_new_row, read_cat_file


def test_find_new_row_detects_addition():
    array1 = [[1, 0.0, 100.0, 200.0], [2, 0.0, 300.0, 400.0]]
    array2 = [[1, 0.0, 100.0, 200.0], [2, 0.0, 300.0, 400.0], [3, 0.0, 500.0, 600.0]]
    new = find_new_row(array1, array2)
    assert len(new) == 1
    assert new[0][2] == 500.0
    assert new[0][3] == 600.0


def test_find_new_row_no_new():
    array1 = [[1, 0.0, 100.0, 200.0], [2, 0.0, 300.0, 400.0]]
    array2 = [[1, 0.0, 100.0, 200.0], [2, 0.0, 300.0, 400.0]]
    new = find_new_row(array1, array2)
    assert len(new) == 0


def test_find_new_row_rounds_coordinates():
    array1 = [[1, 0.0, 100.4, 200.4]]
    # Same position within rounding — should not appear as new
    array2 = [[1, 0.0, 100.6, 200.6]]
    new = find_new_row(array1, array2)
    # 100.4 rounds to 100, 100.6 rounds to 101 — these are different, so new row found
    assert len(new) == 1


def test_find_new_row_value1_correct_type():
    # Verifies the int(np.round(...)) fix: value1 must be comparable to value2 (both int tuples)
    array1 = [[1, 0.0, 99.7, 199.7]]
    array2 = [[1, 0.0, 100.0, 200.0]]
    new = find_new_row(array1, array2)
    # 99.7 rounds to 100, 199.7 rounds to 200 — matches array2
    assert len(new) == 0


def test_check_for_matches_finds_unmatched():
    reference = [[1, 0.0, 100.0, 200.0], [2, 0.0, 300.0, 400.0]]
    science = [[1, 0.0, 100.0, 200.0], [3, 0.0, 500.0, 600.0]]
    new = check_for_matches(reference, science)
    assert len(new) == 1
    assert list(new[0]) == [500.0, 600.0]


def test_check_for_matches_all_matched():
    reference = [[1, 0.0, 100.0, 200.0], [2, 0.0, 300.0, 400.0]]
    science = [[1, 0.0, 101.0, 201.0], [2, 0.0, 301.0, 401.0]]  # within r=4
    new = check_for_matches(reference, science)
    assert len(new) == 0


def test_read_cat_file(tmp_path):
    cat_content = """\
# comment line
# another comment
1 0.5 100.0 200.0 25.0
2 1.5 300.0 400.0 22.0
"""
    cat_file = tmp_path / "test.cat"
    cat_file.write_text(cat_content)
    data = read_cat_file(str(cat_file))
    assert len(data) == 2
    assert data[0][0] == 1
    assert data[0][1] == 0.5
    assert data[1][0] == 2
