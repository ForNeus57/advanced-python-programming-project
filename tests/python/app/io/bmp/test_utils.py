import pytest

from app.io.bmp import compute_padding


@pytest.mark.parametrize("width,expected", [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 0),
    (17, 1),
    (18, 2),
    (19, 3),
    (20, 0),
])
def test_compute_padding(width: int, expected: int) -> None:
    assert compute_padding(width) == expected
