from io import BytesIO
from typing import BinaryIO

import pytest

from app.io.bmp import BMPChecker
from app.io.known_format import KnownFormat


def test_bmp_checker_type() -> None:
    assert KnownFormat.BMP == BMPChecker().type()


@pytest.mark.parametrize('input_data', [
    BytesIO(b'BM'),
    BytesIO(b'BMda'),
    BytesIO(b'BMasjda'),
    BytesIO(b'BMsadjklasjda'),
])
def test_bmp_checker_check_format_true(input_data: BinaryIO) -> None:
    checker = BMPChecker()
    assert checker.check_format(input_data) == True
    assert KnownFormat.BMP == BMPChecker().type()


@pytest.mark.parametrize('input_data', [
    BytesIO(b''),
    BytesIO(b'B'),
    BytesIO(b'M'),
    BytesIO(b'MB'),
    BytesIO(b'asdadasd'),
    BytesIO(b'dasda'),
])
def test_bmp_checker_check_format_false(input_data: BinaryIO) -> None:
    checker = BMPChecker()
    assert checker.check_format(input_data) == False
    assert KnownFormat.BMP == BMPChecker().type()


# @pytest.mark.parametrize('input_file', [
#     ''
# ])
