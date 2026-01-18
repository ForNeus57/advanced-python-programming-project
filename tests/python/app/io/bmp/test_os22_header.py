import pytest

from app.error.invalid_format_exception import InvalidFormatException
from app.io.bmp import DIBInfoHeader, DIBOS22Header


def test_bmp_header_from_default() -> None:
    default_header = DIBOS22Header.from_default()
    expected_header = DIBOS22Header(1, 8, DIBInfoHeader.from_default())

    assert default_header == expected_header
    assert len(default_header) == len(expected_header)
    assert len(default_header) == 28
    assert bytes(default_header) == bytes(expected_header)


@pytest.mark.parametrize("data,expected_header", [
    (b'\x01\x00\x18\x00', DIBOS22Header(1, 24),),           # https://en.wikipedia.org/wiki/BMP_file_format#Example_1
    (b'\x01\x00 \x00', DIBOS22Header(1, 32),),              # https://en.wikipedia.org/wiki/BMP_file_format#Example_2
])
def test_bmp_header_from_bytes(data, expected_header) -> None:
    constructed_obj = DIBOS22Header.from_bytes(data)

    assert constructed_obj == expected_header
    assert bytes(constructed_obj) == bytes(expected_header)
    assert bytes(constructed_obj) == data


@pytest.mark.parametrize("planes,bits_per_pixel", [
    (123, 213),
    (0, 213),
    (2, 213),
    (1, 3),
    (1, 0),
    (1, -1),
])
def test_bmp_header_invalid_signature_ints(planes: int, bits_per_pixel: int) -> None:
    with pytest.raises(InvalidFormatException):
        DIBOS22Header(planes,
                      bits_per_pixel)


@pytest.mark.parametrize('planes', [
    1
])
@pytest.mark.parametrize('bits_per_pixel', [
    1,
    4,
    8,
    16,
    24,
    32,
])
def test_bmp_header_length_no_trailer_short(planes: int, bits_per_pixel: int) -> None:
    assert len(DIBOS22Header(planes, bits_per_pixel)) == 4


@pytest.mark.parametrize('planes', [
    1
])
@pytest.mark.parametrize('bits_per_pixel', [
    1,
    4,
    8,
    16,
    24,
    32,
])
@pytest.mark.parametrize('trailer', [
    DIBInfoHeader.from_default(),
    DIBInfoHeader.from_bytes(b'\x00\x00\x00\x00\x10\x00\x00\x00\x13\x0b\x00\x00\x13\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),
    DIBInfoHeader.from_bytes(b'\x03\x00\x00\x00 \x00\x00\x00\x13\x0b\x00\x00\x13\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),
])
def test_bmp_header_length_no_trailer(planes: int, bits_per_pixel: int, trailer: DIBInfoHeader) -> None:
    assert len(DIBOS22Header(planes, bits_per_pixel, trailer)) == 28