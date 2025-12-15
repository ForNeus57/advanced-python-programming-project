"""Module providing serialization and deserialization for BMP format (https://en.wikipedia.org/wiki/BMP_file_format)"""

import struct
from enum import IntEnum
from typing import final, BinaryIO, override, ClassVar
from dataclasses import dataclass

import numpy as np

from app.error.invalid_format_exception import InvalidFormatException
from app.image.image import Image
from app.io.format_reader import IFormatReader
from app.io.format_writer import IFormatWriter


class DBIHeaderType(IntEnum):
    """Enum containing all the possible DBI headers and their lengths"""

    BITMAP_CORE_HEADER = 12
    OS22X_BITMAP_HEADER = 16
    BITMAP_INFO_HEADER = 40
    BITMAP_V2_INFO_HEADER = 52
    BITMAP_V3_INFO_HEADER = 56
    BITMAP_V4_HEADER = 108
    BITMAP_V5_HEADER = 124


class Signature(IntEnum):
    """Enum containing all possible signature values"""

    BM = 16973
    BA = 16961
    CI = 17225
    CP = 17232
    IC = 18755
    PT = 20564


@dataclass(slots=True)
class BitmapFileHeader:
    """Implements the struct for the Bitmap file header"""

    HEADER_LENGTH: ClassVar[int] = 14

    signature: int
    file_size: int
    reserved_1: int
    reserved_2: int
    file_offset_to_pixel_array: int

    @classmethod
    def from_bytes(cls, data: bytes) -> 'BitmapFileHeader':
        if len(data) < cls.HEADER_LENGTH:
            raise InvalidFormatException(f"Header too short, received: {len(data)} instead of {cls.HEADER_LENGTH}")

        return cls(*struct.unpack('>HIHHI', data))

    def __post_init__(self) -> None:
        if self.signature not in set(e.value for e in Signature):
            raise InvalidFormatException("Invalid signature")

        if self.file_size < self.HEADER_LENGTH + DBIHeaderType.BITMAP_CORE_HEADER:
            raise InvalidFormatException("File too short to parse the next data")

        if self.file_offset_to_pixel_array > self.file_size:
            raise InvalidFormatException("Invalid offset to pixel array")


@dataclass(slots=True)
class BMP:
    header: BitmapFileHeader


@final
class BMPReader(IFormatReader):
    """Class that deserializes BMP format to Image"""

    @override
    def read_format(self, file: BinaryIO) -> Image:
        header = BitmapFileHeader.from_bytes(data=file.read(BitmapFileHeader.HEADER_LENGTH))

        dib_header_size = file.read(4)
        dib_header_size, = struct.unpack('I', dib_header_size)
        assert dib_header_size in (12, 64, 16, 40, 52, 56, 108, 124)
        assert dib_header_size == 40  # BITMAPINFOHEADER

        dib_header_no_size = file.read(dib_header_size - 4)
        image_width, image_height, panes, bits_per_pixel = struct.unpack('iiHH', dib_header_no_size[:12])
        assert panes == 1
        assert bits_per_pixel in (1, 4, 8, 16, 24, 32)

        compression_method, raw_bitmap_data_size, horizontal_resolution, vertical_resolution, \
            num_colors, num_important_colors = \
            struct.unpack('IIiiII', dib_header_no_size[12:])
        assert compression_method == 0
        assert raw_bitmap_data_size != 0

        padding = (4 - ((3 * image_width) % 4)) % 4
        row_size = ((bits_per_pixel * image_width + 31) // 32) * 4

        image_bytes = bytearray()
        for _ in range(image_height):
            image_bytes += file.read(row_size)[:row_size - padding]

        num_colors_end = bits_per_pixel // 8
        return Image(data=np.frombuffer(bytes(image_bytes),
                                        dtype=np.uint8).reshape(image_height, image_width, num_colors_end))


@final
class BMPWriter(IFormatWriter):
    """Class that serializes Image to BMP format"""

    @override
    def write_format(self, file: BinaryIO, input_image: Image) -> None:
        input_arr = input_image.data

        image_height, image_width, num_colors = input_arr.shape
        bits_per_pixel = num_colors * 8
        padding = (4 - ((3 * image_width) % 4)) % 4
        row_size = ((bits_per_pixel * image_width + 31) // 32) * 4
        raw_bitmap_data_size = row_size * image_height

        file_size = 54 + raw_bitmap_data_size

        file.write(struct.pack('BB', 0x42, 0x4D))  # signature
        file.write(struct.pack('I', file_size))  # file_size
        file.write(struct.pack('HH', 0, 0))  # reserved1 & reserved2
        file.write(struct.pack('I', 54))  # file_offset_to_pixel_array

        file.write(struct.pack('I', 40))  # dbi header size
        file.write(struct.pack('iiHH', image_width, image_height, 1, bits_per_pixel))
        file.write(struct.pack('IIiiII', 0, raw_bitmap_data_size, 2834, 2834, 0, 0))

        for i in range(image_height):
            file.write(input_arr[i].tobytes())
            file.write(bytes([0] * padding))
