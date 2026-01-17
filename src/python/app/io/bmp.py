"""Module providing serialization and deserialization for BMP format (https://en.wikipedia.org/wiki/BMP_file_format)"""

import struct
from collections.abc import Sized
from enum import IntEnum
from typing import final, BinaryIO, override, ClassVar, Optional, Final
from dataclasses import dataclass, field, astuple

import numpy as np

from app.error.invalid_format_exception import InvalidFormatException
from app.image.image import Image
from app.io.format_checker import IFormatChecker, check_compare
from app.io.known_format import KnownFormat
from app.io.format_reader import IFormatReader
from app.io.format_writer import IFormatWriter


def compute_padding(width: int) -> int:
    """Computes the number of bytes that need to be added to end of the image row"""

    windows_32_dword_len: Final = 4

    return (windows_32_dword_len - (((windows_32_dword_len - 1) * width) % windows_32_dword_len)) % windows_32_dword_len


@final
class BMPChecker(IFormatChecker):
    """Class that checks if the BMP signature is present"""

    @override
    def check_format(self, file: BinaryIO) -> bool:
        return check_compare(file, '424D')

    @override
    def type(self) -> KnownFormat:
        return KnownFormat.BMP


class DIBHeaderType(IntEnum):
    """Enum containing all the possible DIB headers and their lengths"""

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


class CompressionMethod(IntEnum):
    """Bitmap compression method. https://en.wikipedia.org/wiki/BMP_file_format#Compression"""

    BI_RGB = 0
    BI_RLE8 = 1
    BI_RLE4 = 2
    BI_BITFIELDS = 3
    BI_JPEG = 4
    BI_PNG = 5
    BI_ALPHA_BITFIELDS = 6
    BI_CMYK = 11
    BI_CMYK_RLE8 = 12
    BI_CMYK_RLE4 = 13


@dataclass(slots=True)
class BitmapFileHeader(Sized):
    """Implements the struct for the Bitmap file header"""

    HEADER_LENGTH: ClassVar[int] = 14

    signature: int
    file_size: int
    reserved_1: int
    reserved_2: int
    file_offset_to_pixel_array: int

    @classmethod
    def from_bytes(cls, data: bytes) -> 'BitmapFileHeader':
        """Additional constructor that serializes the BMP format signature"""

        if len(data) < cls.HEADER_LENGTH:
            raise InvalidFormatException(f"Header too short, received: {len(data)} instead of {cls.HEADER_LENGTH}")

        return cls(*struct.unpack('>HIHHI', data))

    @classmethod
    def from_default(cls, dib_size: int, image_data_size: int) -> 'BitmapFileHeader':
        """Additional constructor that create the BMP header with correct file length"""

        return cls(signature=Signature.BM.value,
                   file_size=cls.HEADER_LENGTH + dib_size + image_data_size,
                   reserved_1=0,
                   reserved_2=0,
                   file_offset_to_pixel_array=cls.HEADER_LENGTH + dib_size)

    def __post_init__(self) -> None:
        if self.signature not in set(e.value for e in Signature):
            raise InvalidFormatException("Invalid signature")

        if self.file_size < self.HEADER_LENGTH + DIBHeaderType.BITMAP_CORE_HEADER:
            raise InvalidFormatException("File too short to parse the next data")

        if self.file_offset_to_pixel_array > self.file_size:
            raise InvalidFormatException("Invalid offset to pixel array")

    def __bytes__(self) -> bytes:
        return struct.pack('>HIHHI', *astuple(self))

    def __len__(self) -> int:
        return self.HEADER_LENGTH


@dataclass(slots=True, frozen=True)
class DIBInfoHeader(Sized):
    """Class that represents BMP file DIB Info header specific fields"""

    BASE_LENGTH_BYTES: ClassVar[int] = 24

    compression: int
    image_size: int
    x_pixels_in_meters: int
    y_pixels_in_meters: int
    colors_in_color_table: int
    important_color_count: int

    @classmethod
    def from_bytes(cls, data: bytes) -> 'DIBInfoHeader':
        """Additional constructor for the class to create the object from the raw bytes"""

        compression, image_size, x_pixels_in_meters, y_pixels_in_meters, colors_in_color_table, important_color_count =\
            struct.unpack('IIiiII', data)

        return cls(compression=compression,
                   image_size=image_size,
                   x_pixels_in_meters=x_pixels_in_meters,
                   y_pixels_in_meters=y_pixels_in_meters,
                   colors_in_color_table=colors_in_color_table,
                   important_color_count=important_color_count)

    @classmethod
    def from_default(cls) -> 'DIBInfoHeader':
        """Additional constructor for the class to create the object with default values"""

        return cls(compression=CompressionMethod.BI_RGB.value,
                   image_size=0,
                   x_pixels_in_meters=200,
                   y_pixels_in_meters=200,
                   colors_in_color_table=0,
                   important_color_count=0)

    def __post_init__(self) -> None:
        if self.compression != CompressionMethod.BI_RGB.value:
            raise NotImplementedError

        if self.x_pixels_in_meters <= 0:
            raise InvalidFormatException('Invalid format')

        if self.y_pixels_in_meters <= 0:
            raise InvalidFormatException('Invalid format')

        if self.colors_in_color_table < 0:
            raise InvalidFormatException('Invalid format')

        if self.important_color_count < 0:
            raise InvalidFormatException('Invalid format')

    def __bytes__(self) -> bytes:
        return struct.pack('IIiiII',
                           self.compression,
                           self.image_size,
                           self.x_pixels_in_meters,
                           self.y_pixels_in_meters,
                           self.colors_in_color_table,
                           self.important_color_count)

    def __len__(self) -> int:
        return self.BASE_LENGTH_BYTES


@dataclass(slots=True, frozen=True)
class DIBOS22Header(Sized):
    """Class that represents BMP file DIB OS22 header specific fields"""

    BASE_LENGTH_BYTES: ClassVar[int] = 4

    planes: int
    bits_per_pixel: int
    info_header: Optional[DIBInfoHeader] = field(default=None)

    @classmethod
    def from_bytes(cls, data: bytes, info_header: Optional[DIBInfoHeader] = None) -> 'DIBOS22Header':
        """Additional constructor that allows to create this class object from the raw bytes"""

        planes, bits_per_pixel = struct.unpack('HH', data)
        return cls(planes=planes,
                   bits_per_pixel=bits_per_pixel,
                   info_header=info_header)

    @classmethod
    def from_default(cls) -> 'DIBOS22Header':
        """Additional constructor that allows to create this class object using default initialisation"""

        return DIBOS22Header(planes=1,
                             bits_per_pixel=8,
                             info_header=DIBInfoHeader.from_default())

    def __post_init__(self) -> None:
        if self.planes != 1:
            raise InvalidFormatException('Invalid format')

        if self.bits_per_pixel not in {1, 4, 8, 16, 24, 32}:
            raise InvalidFormatException('Invalid format')

    def __bytes__(self) -> bytes:
        return struct.pack('HH', self.planes, self.bits_per_pixel)\
            + (b'' if self.info_header is None else bytes(self.info_header))

    def __len__(self) -> int:
        return self.BASE_LENGTH_BYTES + 0 if self.info_header is None else len(self.info_header)


@dataclass(slots=True, frozen=True)
class DIBCoreHeader(Sized):
    """Class that represents BMP file DIB core header specific fields that must always be present in the file"""

    HEADER_SIZE_LEN: ClassVar[int] = 4
    BASE_LENGTH_BYTES: ClassVar[int] = 12

    dib_header_size: int
    image_width: int
    image_height: int
    os22_header: Optional[DIBOS22Header] = field(default=None)

    @classmethod
    def from_bytes(cls, file: BinaryIO) -> 'DIBCoreHeader':
        """Additional constructor that allows to create this class object from the raw bytes"""

        dib_header_size = file.read(cls.HEADER_SIZE_LEN)
        dib_header_size, = struct.unpack('I', dib_header_size)
        dib_header_no_size = file.read(cls.BASE_LENGTH_BYTES - cls.HEADER_SIZE_LEN)

        match dib_header_size:
            case DIBHeaderType.BITMAP_CORE_HEADER.value:
                image_width, image_height = struct.unpack('ii', dib_header_no_size)
                return cls(dib_header_size=dib_header_size,
                           image_width=image_width,
                           image_height=image_height)

            case DIBHeaderType.OS22X_BITMAP_HEADER.value:
                image_width, image_height = struct.unpack('ii', dib_header_no_size)
                return cls(dib_header_size=dib_header_size,
                           image_width=image_width,
                           image_height=image_height,
                           os22_header=DIBOS22Header.from_bytes(file.read(DIBOS22Header.BASE_LENGTH_BYTES)))

            case DIBHeaderType.BITMAP_INFO_HEADER.value:
                image_width, image_height = struct.unpack('ii', dib_header_no_size)
                os_22_header_raw_data = file.read(DIBOS22Header.BASE_LENGTH_BYTES)
                info_header_raw_bytes = file.read(DIBInfoHeader.BASE_LENGTH_BYTES)

                return cls(dib_header_size=dib_header_size,
                           image_width=image_width,
                           image_height=image_height,
                           os22_header=DIBOS22Header.from_bytes(os_22_header_raw_data,
                                                                info_header=DIBInfoHeader.from_bytes(
                                                                    info_header_raw_bytes)))

        raise NotImplementedError

    def __bytes__(self) -> bytes:
        return struct.pack('Iii', self.dib_header_size, self.image_width, self.image_height)\
            + (b'' if self.os22_header is None else bytes(self.os22_header))

    def __len__(self) -> int:
        return self.BASE_LENGTH_BYTES + 0 if self.os22_header is None else len(self.os22_header)

    def __post_init__(self) -> None:
        if self.dib_header_size not in {12, 16, 40, 52, 56, 108, 124}:
            raise InvalidFormatException(f'Wrong: {self.dib_header_size=}')

        if self.dib_header_size > 40:
            raise NotImplementedError

        if self.image_width <= 0:
            raise InvalidFormatException(f'Wrong: {self.image_width=}')

        if self.image_height <= 0:
            raise InvalidFormatException(f'Wrong: {self.image_height=}')

    def get_bits_per_pixel(self) -> int:
        """Getter for that bits per pixel field that handles the case if the os22 header is not present"""

        return 8 if self.os22_header is None else self.os22_header.bits_per_pixel


@dataclass(slots=True)
class BMP(Sized):
    """Class that represents the BMP file in a structured way"""

    header: BitmapFileHeader
    dib_header: DIBCoreHeader
    color_table: Optional[bytes]
    image_data: bytes

    @classmethod
    def from_bytes(cls, file: BinaryIO) -> 'BMP':
        """Additional constructor that allows to create this class object from the raw bytes"""

        header = BitmapFileHeader.from_bytes(data=file.read(BitmapFileHeader.HEADER_LENGTH))
        dib_header = DIBCoreHeader.from_bytes(file)

        return cls(header=header,
                   dib_header=dib_header,
                   color_table=None,
                   image_data=file.read(header.file_size - header.file_offset_to_pixel_array))

    @classmethod
    def from_ndarray(cls, data: np.ndarray) -> 'BMP':
        """Additional constructor that allows to create this class object from numpy array"""

        image_height, image_width, _ = data.shape
        padding = compute_padding(image_width)

        image_data = bytearray()
        for i in range(image_height):
            image_data += data[i].tobytes() + bytes([0] * padding)

        os22_header = DIBOS22Header.from_default()
        dib_header = DIBCoreHeader(dib_header_size=DIBCoreHeader.BASE_LENGTH_BYTES + len(os22_header),
                                   image_width=image_width,
                                   image_height=image_height,
                                   os22_header=os22_header)
        header = BitmapFileHeader.from_default(dib_size=len(dib_header),
                                               image_data_size=len(image_data))

        return cls(header=header,
                   dib_header=dib_header,
                   color_table=None,
                   image_data=image_data)

    def to_numpy(self) -> np.ndarray:
        """Converter to a numpy array from a bitmap data"""

        width = self.dib_header.image_width
        height = self.dib_header.image_height
        bits_per_pixel = self.dib_header.get_bits_per_pixel()

        padding = self.get_padding()
        row_size = self.get_row_size()

        image_bytes = bytearray()
        for height_idx in range(height):
            image_bytes += self.image_data[height_idx * row_size: ((height_idx + 1) * row_size) - padding]

        num_colors_end = bits_per_pixel // 8
        return np.frombuffer(bytes(image_bytes),
                             dtype=np.uint8).reshape(height, width, num_colors_end)

    def __post_init__(self) -> None:
        if len(self.image_data) != self.header.file_size - self.header.file_offset_to_pixel_array:
            raise InvalidFormatException('Invalid argument')

    def __bytes__(self) -> bytes:
        return bytes(self.header)\
            + bytes(self.dib_header)\
            + (b'' if self.color_table is None else self.color_table)\
            + self.image_data

    def __len__(self) -> int:
        return len(self.header) + len(self.dib_header) + len(self.image_data)

    def get_padding(self) -> int:
        """Method that computes the number of bytes that are appended at the end of all the row"""

        width = self.dib_header.image_width
        return compute_padding(width)

    def get_row_size(self) -> int:
        """https://en.wikipedia.org/wiki/BMP_file_format#Pixel_storage"""

        width = self.dib_header.image_width
        bits_per_pixel = self.dib_header.get_bits_per_pixel()

        return ((bits_per_pixel * width + 31) // 32) * 4


@final
class BMPReader(IFormatReader):     # pylint: disable=too-few-public-methods
    """Class that deserializes BMP format to Image"""

    @override
    def read_format(self, file: BinaryIO) -> Image:
        bmp = BMP.from_bytes(file)
        return Image(data=bmp.to_numpy())

        # dib_header_size = file.read(4)
        # dib_header_size, = struct.unpack('I', dib_header_size)
        # assert dib_header_size in (12, 64, 16, 40, 52, 56, 108, 124)
        # assert dib_header_size == 40  # BITMAPINFOHEADER
        #
        # dib_header_no_size = file.read(dib_header_size - 4)
        # image_width, image_height, panes, bits_per_pixel = struct.unpack('iiHH', dib_header_no_size[:12])
        # assert panes == 1
        # assert bits_per_pixel in (1, 4, 8, 16, 24, 32)
        #
        # compression_method, raw_bitmap_data_size, horizontal_resolution, vertical_resolution, \
        #     num_colors, num_important_colors = \
        #     struct.unpack('IIiiII', dib_header_no_size[12:])
        # assert compression_method == 0
        # assert raw_bitmap_data_size != 0
        #
        # padding = (4 - ((3 * image_width) % 4)) % 4
        # row_size = ((bits_per_pixel * image_width + 31) // 32) * 4
        #
        # image_bytes = bytearray()
        # for _ in range(image_height):
        #     image_bytes += file.read(row_size)[:row_size - padding]
        #
        # num_colors_end = bits_per_pixel // 8
        # return Image(data=np.frombuffer(bytes(image_bytes),
        #                                 dtype=np.uint8).reshape(image_height, image_width, num_colors_end))


@final
class BMPWriter(IFormatWriter):     # pylint: disable=too-few-public-methods
    """Class that serializes Image to BMP format"""

    @override
    def write_format(self, file: BinaryIO, input_image: Image) -> None:
        bmp = BMP.from_ndarray(input_image.data)
        file.write(bytes(bmp))

        # input_arr = input_image.data
        #
        # image_height, image_width, num_colors = input_arr.shape
        # bits_per_pixel = num_colors * 8
        # padding = (4 - ((3 * image_width) % 4)) % 4
        # row_size = ((bits_per_pixel * image_width + 31) // 32) * 4
        # raw_bitmap_data_size = row_size * image_height
        #
        # file_size = 54 + raw_bitmap_data_size
        #
        # file.write(b''.join((
        #     struct.pack('BB', 0x42, 0x4D),      # signature
        #     struct.pack('I', file_size),        # file_size
        #     struct.pack('HH', 0, 0),            # reserved1 & reserved2
        #     struct.pack('I', 54),               # file_offset_to_pixel_array
        #     struct.pack('I', 40),               # dbi header size
        #     struct.pack('iiHH', image_width, image_height, 1, bits_per_pixel),
        #     struct.pack('IIiiII', 0, raw_bitmap_data_size, 2834, 2834, 0, 0),
        # )))
        #
        # for i in range(image_height):
        #     file.write(input_arr[i].tobytes() + bytes([0] * padding))
