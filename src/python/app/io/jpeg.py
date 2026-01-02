"""Module for IO operations related to Jpeg encoding"""

from typing import BinaryIO, override, final

import numpy as np

from app.image.image import Image
from app.io.format_checker import IFormatChecker, check_compare
from app.io.known_format import KnownFormat
from app.io.format_reader import IFormatReader
from app.io.format_writer import IFormatWriter

@final
class JPEGChecker(IFormatChecker):
    """Class comparing the file signature to deduce file format"""

    @override
    def check_format(self, file: BinaryIO) -> bool:
        return check_compare(file, 'FFD8FFDB')\
                or check_compare(file, 'FFD8FFE000104A4649460001')\
                or check_compare(file, 'FFD8FFEE')\
                or check_compare(file, 'FFD8FFE0')\
                or check_compare(file, '0000000C6A5020200D0A870A')\
                or check_compare(file, 'FF4FFF51')

    @override
    def type(self) -> KnownFormat:
        return KnownFormat.JPEG


@final
class JPEGReader(IFormatReader):        # pylint: disable=too-few-public-methods
    """Class that deserializes JPEG format to Image"""

    @override
    def read_format(self, file: BinaryIO) -> Image:
        import app.fast     # pylint: disable=import-outside-toplevel
        return Image(data=app.fast.decode_jpeg(file.read()))


@final
class JPEGWriter(IFormatWriter):        # pylint: disable=too-few-public-methods
    """Class that serializes Image to JPEG format"""

    @override
    def write_format(self, file: BinaryIO, input_image: Image) -> None:
        import app.fast     # pylint: disable=import-outside-toplevel
        file.write(app.fast.encode_jpeg(np.flip(input_image.data[:, :, ::-1], axis=0).copy()))
