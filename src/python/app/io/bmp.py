import struct
from enum import IntEnum
from typing import final, BinaryIO, override

import numpy as np

from app.image.image import Image
from app.io.format_reader import FormatReader
from app.io.format_writer import FormatWriter


class DBIHeader(IntEnum):
    BITMAP_CORE_HEADER = 12
    OS22X_BITMAP_HEADER = 16
    BITMAP_INFO_HEADER = 40
    BITMAP_V2_INFO_HEADER = 52
    BITMAP_V3_INFO_HEADER = 56
    BITMAP_V4_HEADER = 108
    BITMAP_V5_HEADER = 124


@final
class BMPReader(FormatReader):

    @override
    def read_format(self, file: BinaryIO) -> Image:
        header = file.read(14)
        assert len(header) == 14

        signature_first, signature_second = struct.unpack('BB', header[:2])
        # signature_first, signature_second = hex(signature_first), hex(signature_second)
        assert (signature_first, signature_second) in [(0x42, 0x4D), (0x42, 0x41), (0x43, 0x49), (0x43, 0x50),
                                                       (0x49, 0x43), (0x50, 0x54)]

        file_size, = struct.unpack('I', header[2:6])
        res1, res2 = struct.unpack('HH', header[6:10])
        file_offset_to_pixel_array, = struct.unpack('I', header[10:])

        dib_header_size = file.read(4)
        dib_header_size, = struct.unpack('I', dib_header_size)
        assert dib_header_size in (12, 64, 16, 40, 52, 56, 108, 124)
        assert dib_header_size == 40  # BITMAPINFOHEADER

        dib_header_no_size = file.read(dib_header_size - 4)
        image_width, image_height, panes, bits_per_pixel = struct.unpack('iiHH', dib_header_no_size[:12])
        assert panes == 1
        assert bits_per_pixel in (1, 4, 8, 16, 24, 32)

        compression_method, raw_bitmap_data_size, horizontal_resolution, vertical_resolution, num_colors, num_important_colors = \
            struct.unpack('IIiiII', dib_header_no_size[12:])
        assert compression_method == 0
        assert raw_bitmap_data_size != 0

        padding = (4 - ((3 * image_width) % 4)) % 4
        row_size = ((bits_per_pixel * image_width + 31) // 32) * 4

        image_bytes = bytearray()
        for _ in range(image_height):
            image_bytes += file.read(row_size)[:row_size - padding]

        num_colors_end = bits_per_pixel // 8
        return Image(data=np.flip(
            np.flip(
                np.frombuffer(bytes(image_bytes), dtype=np.uint8).reshape(image_height, image_width, num_colors_end)[:, :, ::-1],
                axis=0
            ),
            axis=1)
        )


@final
class BMPWriter(FormatWriter):

    def write_format(self, file: BinaryIO, input_image: Image) -> None:
        input_arr = input_image.data
        input_arr = np.flip(np.flip(input_arr[:, :, ::-1], axis=1), axis=0)

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
