import pytest

from app.error.invalid_format_exception import InvalidFormatException
from app.io.bmp import BitmapFileHeader, DIBHeaderType, Signature


@pytest.mark.parametrize("dib_header_size", [
    DIBHeaderType.BITMAP_CORE_HEADER.value,
    DIBHeaderType.OS22X_BITMAP_HEADER.value,
    DIBHeaderType.BITMAP_INFO_HEADER.value,
    DIBHeaderType.BITMAP_V2_INFO_HEADER.value,
    DIBHeaderType.BITMAP_V3_INFO_HEADER.value,
    DIBHeaderType.BITMAP_V4_HEADER.value,
    DIBHeaderType.BITMAP_V5_HEADER.value,
])
@pytest.mark.parametrize("image_data_size", [
    0,
    1,
    100,
    200,
    672,
])
def test_bmp_header_from_default(dib_header_size, image_data_size) -> None:
    default_header = BitmapFileHeader.from_default(dib_header_size, image_data_size)
    expected_header = BitmapFileHeader(Signature.BM.value,
                                       BitmapFileHeader.HEADER_LENGTH + dib_header_size + image_data_size,
                                       0,
                                       0,
                                       BitmapFileHeader.HEADER_LENGTH + dib_header_size)

    assert default_header == expected_header
    assert len(default_header) == len(expected_header)
    assert len(BitmapFileHeader.from_default(DIBHeaderType.BITMAP_CORE_HEADER.value, 0)) == 14
    assert bytes(default_header) == bytes(expected_header)


@pytest.mark.parametrize("data,expected_header", [
    (b'BMF\x00\x00\x00\x00\x00\x00\x006\x00\x00\x00',    BitmapFileHeader(Signature.BM, 70, 0, 0, 54),),                # https://en.wikipedia.org/wiki/BMP_file_format#Example_1
    (b'BM\x9a\x00\x00\x00\x00\x00\x00\x00z\x00\x00\x00', BitmapFileHeader(Signature.BM, 154, 0, 0, 122),),              # https://en.wikipedia.org/wiki/BMP_file_format#Example_2
])
def test_bmp_header_from_bytes(data, expected_header) -> None:
    constructed_obj = BitmapFileHeader.from_bytes(data)

    assert constructed_obj == expected_header
    assert bytes(constructed_obj) == bytes(expected_header)
    assert bytes(constructed_obj) == data


@pytest.mark.parametrize("signature,file_size,reserved_1,reserved_2,file_offset_to_pixel_array", [
    (123, 213, 3342, 4535, 542543),
    (Signature.BM.value, 213, 3342, 4535, 542543),
    (Signature.BM.value, 0, 3342, 4535, 542543),
])
def test_bmp_header_invalid_signature_ints(signature: int, file_size: int, reserved_1: int, reserved_2: int, file_offset_to_pixel_array: int) -> None:
    with pytest.raises(InvalidFormatException):
        BitmapFileHeader(signature, file_size, reserved_1, reserved_2, file_offset_to_pixel_array)


@pytest.mark.parametrize("data", [
    b'',
    b'sadfjfs',
    b'BM',
    b'fsdjkhasfdjf'
])
def test_bmp_header_invalid_signature(data: bytes) -> None:
    with pytest.raises(InvalidFormatException):
        BitmapFileHeader.from_bytes(data)


def test_bmp_header_invalid_from_file_png(resource_png) -> None:
    with pytest.raises(InvalidFormatException):
        BitmapFileHeader.from_bytes(resource_png.read(BitmapFileHeader.HEADER_LENGTH))


def test_bmp_header_invalid_from_file_jpg(resource_jpg) -> None:
    with pytest.raises(InvalidFormatException):
        BitmapFileHeader.from_bytes(resource_jpg.read(BitmapFileHeader.HEADER_LENGTH))


def test_bmp_header_invalid_from_file_avif(resource_avif) -> None:
    with pytest.raises(InvalidFormatException):
        BitmapFileHeader.from_bytes(resource_avif.read(BitmapFileHeader.HEADER_LENGTH))
