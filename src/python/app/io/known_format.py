"""Module holding an enum for all the """

import enum


class KnownFormat(enum.Enum):
    """Enum providing all the image formats that are supported by the program"""

    BMP = 0

    PNG = enum.auto()

    JPEG = enum.auto()

    PBM = enum.auto()
    PGM = enum.auto()
    PPM = enum.auto()

    @classmethod
    def from_string(cls, data: str) -> 'KnownFormat':
        """Additional constructor to convert string into the KnownFormat enum object"""

        return cls[data.upper()]

    @classmethod
    def get_available_formats(cls) -> list[str]:
        """Return default format for commandline to use"""

        return [e.name.lower() for e in cls]
