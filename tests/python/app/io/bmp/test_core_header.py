from io import BytesIO
from typing import Optional

import pytest

from app.error.invalid_format_exception import InvalidFormatException
from app.io.bmp import DIBInfoHeader, CompressionMethod, DIBOS22Header, DIBCoreHeader, DIBHeaderType


@pytest.mark.parametrize("data,expected_header", [
    (b'\x0c\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00', DIBCoreHeader(12, 2, 2),),
    (b'\x0c\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00', DIBCoreHeader(12, 4, 2),),
    (b'\x10\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x01\x00\x18\x00', DIBCoreHeader(16, 2, 2, DIBOS22Header(1, 24)),),
    (b'\x10\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x01\x00 \x00', DIBCoreHeader(16, 4, 2, DIBOS22Header(1, 32)),),
    (b'(\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x10\x00\x00\x00\x13\x0b\x00\x00\x13\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', DIBCoreHeader(40, 2, 2, DIBOS22Header(1, 24, DIBInfoHeader(0, 16, 2835, 2835, 0, 0))),),           # https://en.wikipedia.org/wiki/BMP_file_format#Example_1
    (b'(\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x01\x00 \x00\x03\x00\x00\x00 \x00\x00\x00\x13\x0b\x00\x00\x13\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', DIBCoreHeader(40, 4, 2, DIBOS22Header(1, 32, DIBInfoHeader(3, 32, 2835, 2835, 0, 0))),),              # https://en.wikipedia.org/wiki/BMP_file_format#Example_2
])
def test_bmp_header_from_bytes(data: bytes, expected_header: DIBCoreHeader) -> None:
    constructed_obj = DIBCoreHeader.from_bytes(BytesIO(data))

    assert constructed_obj == expected_header
    assert bytes(constructed_obj) == bytes(expected_header)
    assert bytes(constructed_obj) == data
    assert len(constructed_obj) == len(expected_header)


@pytest.mark.parametrize("data", [
    b'\x0e\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00',
    b'\x0d\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00',
])
def test_bmp_header_from_bytes_invalid(data: bytes) -> None:
    with pytest.raises(InvalidFormatException):
        DIBCoreHeader.from_bytes(BytesIO(data))


@pytest.mark.parametrize("dib_header_size,image_width,image_height", [
    (0, 213, 213),
    (23, 213, 213),
    (24, 213, 213),
    (DIBHeaderType.BITMAP_CORE_HEADER.value, 0, 213),
    (DIBHeaderType.OS22X_BITMAP_HEADER.value, -1, 213),
    (DIBHeaderType.BITMAP_INFO_HEADER.value, -99, 213),
    (DIBHeaderType.BITMAP_V2_INFO_HEADER.value, 213, 0),
    (DIBHeaderType.BITMAP_V3_INFO_HEADER.value, 213, -1),
    (DIBHeaderType.BITMAP_V4_HEADER.value, 213, -99),
])
def test_bmp_header_invalid_signature_ints(dib_header_size: int, image_width: int, image_height: int) -> None:
    with pytest.raises(InvalidFormatException):
        DIBCoreHeader(dib_header_size, image_width, image_height)


@pytest.mark.parametrize('dib_header_size', [
    DIBHeaderType.BITMAP_CORE_HEADER.value,
    DIBHeaderType.OS22X_BITMAP_HEADER.value,
    DIBHeaderType.BITMAP_INFO_HEADER.value,
    DIBHeaderType.BITMAP_V2_INFO_HEADER.value,
    DIBHeaderType.BITMAP_V3_INFO_HEADER.value,
    DIBHeaderType.BITMAP_V4_HEADER.value,
    DIBHeaderType.BITMAP_V5_HEADER.value,
])
@pytest.mark.parametrize('image_width', [
    1, 15, 7211, 323,
])
@pytest.mark.parametrize('image_height', [
    1, 15, 7211, 323,
])
@pytest.mark.parametrize('trailer,expected_length', [
    (None, 12,),
    (DIBOS22Header.from_default(), 40,),
    (DIBOS22Header.from_bytes(b'\x01\x00\x18\x00'), 16,),
    (DIBOS22Header.from_bytes(b'\x01\x00 \x00'), 16,),
    (DIBOS22Header.from_default(), 40,),
    (DIBOS22Header.from_bytes(b'\x01\x00\x18\x00', DIBInfoHeader.from_default()), 40,),
    (DIBOS22Header.from_bytes(b'\x01\x00 \x00', DIBInfoHeader.from_default()), 40,),
])
def test_bmp_header_length_no_trailer(dib_header_size: int, image_width: int, image_height: int, trailer: Optional[DIBInfoHeader], expected_length: int) -> None:
    assert len(DIBCoreHeader(dib_header_size, image_width, image_height, trailer)) == expected_length


@pytest.mark.parametrize('dib_header_size', [
    DIBHeaderType.BITMAP_CORE_HEADER.value,
    DIBHeaderType.OS22X_BITMAP_HEADER.value,
    DIBHeaderType.BITMAP_INFO_HEADER.value,
    DIBHeaderType.BITMAP_V2_INFO_HEADER.value,
    DIBHeaderType.BITMAP_V3_INFO_HEADER.value,
    DIBHeaderType.BITMAP_V4_HEADER.value,
    DIBHeaderType.BITMAP_V5_HEADER.value,
])
@pytest.mark.parametrize('image_width', [
    1, 15, 7211, 323,
])
@pytest.mark.parametrize('image_height', [
    1, 15, 7211, 323,
])
@pytest.mark.parametrize('trailer,expected_length', [
    (None, 8,),
    (DIBOS22Header.from_default(), 8,),
    (DIBOS22Header.from_bytes(b'\x01\x00\x18\x00'), 24,),
    (DIBOS22Header.from_bytes(b'\x01\x00 \x00'), 32,),
])
def test_bmp_header_get_bits_per_pixel(dib_header_size: int, image_width: int, image_height: int, trailer: Optional[DIBInfoHeader], expected_length: int) -> None:
    assert DIBCoreHeader(dib_header_size, image_width, image_height, trailer).get_bits_per_pixel() == expected_length
