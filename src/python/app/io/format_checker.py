"""Module defining Checker interface"""

import os
from abc import abstractmethod, ABC
from typing import BinaryIO

from app.io.known_format import KnownFormat


class IFormatChecker(ABC):
    """https://en.wikipedia.org/wiki/List_of_file_signatures"""

    @abstractmethod
    def check_format(self, file: BinaryIO) -> bool:
        """Determines the type of file from its signature"""

    @abstractmethod
    def type(self) -> KnownFormat:
        """Returns the KnownFormat the checker is inspecting"""


def check_compare(file: BinaryIO, signature: str) -> bool:
    """Checks if the file starts with a hex representation of signature"""

    signature_bytes = bytes.fromhex(signature.lower())
    return rest_read_bytes(file, len(signature_bytes)) == signature_bytes

def rest_read_bytes(file: BinaryIO, n: int) -> bytes:
    """Resets the binary stream and reads n bytes"""

    reset_stream(file)
    return file.read(n)

def reset_stream(file: BinaryIO) -> None:
    """Resets the binary interface pointer to the start of the file"""

    file.seek(0, os.SEEK_SET)
