import pytest
import numpy as np

from app.fast import system # type: ignore
from app.fast import numpy_add # type: ignore


def test_system():
    assert 0 == system('ls -la')
    assert 0 != system('false')


numpy_add_values = [
    (np.array([2, 1, 4], dtype=np.double), np.sum([2, 1, 4])),
    (np.array([3, 1, 2], dtype=np.double), np.sum([3, 1, 2])),
    (np.array([10, 24, 11], dtype=np.double), np.sum([10, 24, 11])),
    (np.array([99, 1, 22], dtype=np.double), np.sum([99, 1, 22]))
]


@pytest.mark.parametrize("array1,expected_result", numpy_add_values)
def test_numpy_add(array1, expected_result):
    assert numpy_add(array1) == expected_result
