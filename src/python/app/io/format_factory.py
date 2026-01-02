"""Module implementing routing functions for input image formats"""
import os
from typing import BinaryIO

from app.error.unknown_format_exception import UnknownFormatException
from app.io.bmp import BMPReader, BMPWriter, BMPChecker
from app.io.format_checker import reset_stream
from app.io.format_reader import IFormatReader
from app.io.format_writer import IFormatWriter
from app.io.jpeg import JPEGReader, JPEGWriter, JPEGChecker
from app.io.known_format import KnownFormat
from app.io.png import PNGWriter, PNGReader, PNGChecker


def get_available_formats():
    return [
        BMPChecker(),
        PNGChecker(),
        JPEGChecker(),
    ]


def determine_format(file: BinaryIO) -> KnownFormat:
    for format_checker in get_available_formats():
        if format_checker.check_format(file):
            reset_stream(file)
            return format_checker.type()

    raise UnknownFormatException("The file signature is not recognized as a supported image format")


def get_reader_from_format(data_format: KnownFormat) -> IFormatReader:
    """Factory function for format reader"""

    match data_format:
        case KnownFormat.BMP:
            return BMPReader()

        case KnownFormat.PNG:
            return PNGReader()

        case KnownFormat.JPEG:
            return JPEGReader()

    assert False, "unreachable"


def get_writer_from_format(data_format: KnownFormat) -> IFormatWriter:
    """Factory function for format writer"""

    match data_format:
        case KnownFormat.BMP:
            return BMPWriter()

        case KnownFormat.PNG:
            return PNGWriter()

        case KnownFormat.JPEG:
            return JPEGWriter()

    assert False, "unreachable"
