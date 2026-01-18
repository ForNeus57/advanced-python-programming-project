import pytest

from app.error.invalid_format_exception import InvalidFormatException
from app.io.bmp import DIBInfoHeader, CompressionMethod


def test_bmp_header_from_default() -> None:
    default_header = DIBInfoHeader.from_default()
    expected_header = DIBInfoHeader(CompressionMethod.BI_RGB.value, 1, 200, 200, 0, 0)

    assert default_header == expected_header
    assert len(default_header) == len(expected_header)
    assert len(default_header) == 24
    assert bytes(default_header) == bytes(expected_header)


@pytest.mark.parametrize("data,expected_header", [
    (b'\x00\x00\x00\x00\x10\x00\x00\x00\x13\x0b\x00\x00\x13\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', DIBInfoHeader(CompressionMethod.BI_RGB.value, 16, 2835, 2835, 0, 0),),                                 # https://en.wikipedia.org/wiki/BMP_file_format#Example_1
    (b'\x03\x00\x00\x00 \x00\x00\x00\x13\x0b\x00\x00\x13\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', DIBInfoHeader(CompressionMethod.BI_BITFIELDS.value, 32, 2835, 2835, 0, 0),),              # https://en.wikipedia.org/wiki/BMP_file_format#Example_2
])
def test_bmp_header_from_bytes(data, expected_header) -> None:
    constructed_obj = DIBInfoHeader.from_bytes(data)

    assert constructed_obj == expected_header
    assert bytes(constructed_obj) == bytes(expected_header)
    assert bytes(constructed_obj) == data


@pytest.mark.parametrize("compression,image_size,x_pixels_in_meters,y_pixels_in_meters,colors_in_color_table,important_color_count", [
    (123, 213, 3342, 4535, 542543, 7),
    (CompressionMethod.BI_RGB.value, -1, 3342, 4535, 542543, 7),
    (CompressionMethod.BI_RGB.value, 213, -1, 4535, 542543, 7),
    (CompressionMethod.BI_RGB.value, 2, 3342, -1, 542543, 7),
    (CompressionMethod.BI_RGB.value, 213, 3342, 4535, -1, 7),
    (CompressionMethod.BI_RGB.value, 2, 3342, 4535, 542543, -1),
])
def test_bmp_header_invalid_signature_ints(compression: int, image_size: int, x_pixels_in_meters: int, y_pixels_in_meters: int, colors_in_color_table: int, important_color_count: int) -> None:
    with pytest.raises(InvalidFormatException):
        DIBInfoHeader(compression,
                      image_size,
                      x_pixels_in_meters,
                      y_pixels_in_meters,
                      colors_in_color_table,
                      important_color_count)
