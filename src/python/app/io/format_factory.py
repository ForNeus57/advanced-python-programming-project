import enum

from app.error.unknown_format_exception import UnknownFormatException
from app.io.bmp import BMPReader, BMPWriter
from app.io.format_reader import FormatReader
from app.io.format_writer import FormatWriter


class KnownFormat(enum.Enum):
    BMP = 0

    @classmethod
    def from_string(cls, data_format: str) -> 'KnownFormat':
        match data_format:
            case 'bmp':
                return cls.BMP

            case _:
                raise UnknownFormatException(data_format)

    @classmethod
    def get_available_formats(cls) -> list[str]:
        return [e.name.lower() for e in cls]

    @classmethod
    def default(cls) -> 'KnownFormat':
        return KnownFormat.BMP


def get_reader_from_format(data_format: KnownFormat) -> FormatReader:

    match data_format:
        case KnownFormat.BMP:
            return BMPReader()

        case _:
            assert False, "unreachable"


def get_writer_from_format(data_format: KnownFormat) -> FormatWriter:

    match data_format:
        case KnownFormat.BMP:
            return BMPWriter()

        case _:
            assert False, "unreachable"
