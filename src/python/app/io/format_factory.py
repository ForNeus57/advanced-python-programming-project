"""Module implementing routing functions for input image formats"""

import enum

from app.error.unknown_format_exception import UnknownFormatException
from app.io.bmp import BMPReader, BMPWriter
from app.io.format_reader import IFormatReader
from app.io.format_writer import IFormatWriter


class KnownFormat(enum.Enum):
    """Enum providing all the image formats that are supported by the program"""

    BMP = 0
    PNG = enum.auto()
    PBM = enum.auto()
    PGM = enum.auto()
    PPM = enum.auto()

    @classmethod
    def from_string(cls, data_format: str) -> 'KnownFormat':
        """Additional constructor for this class"""

        match data_format:
            case 'bmp':
                return cls.BMP

            case _:
                raise UnknownFormatException(data_format)

    @classmethod
    def get_available_formats(cls) -> list[str]:
        """Return default format for commandline to use"""

        return [e.name.lower() for e in cls]

    @classmethod
    def default(cls) -> 'KnownFormat':
        """Return default format for commandline to use"""

        return KnownFormat.BMP


def get_reader_from_format(data_format: KnownFormat) -> IFormatReader:
    """Factory function for format reader"""

    match data_format:
        case KnownFormat.BMP:
            return BMPReader()

        case _:
            assert False, "unreachable"


def get_writer_from_format(data_format: KnownFormat) -> IFormatWriter:
    """Factory function for format writer"""

    match data_format:
        case KnownFormat.BMP:
            return BMPWriter()

        case _:
            assert False, "unreachable"
