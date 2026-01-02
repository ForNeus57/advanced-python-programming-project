import os
from abc import abstractmethod, ABC
from typing import BinaryIO

from app.io.known_format import KnownFormat


class IFormatChecker(ABC):
    """https://en.wikipedia.org/wiki/List_of_file_signatures"""

    @abstractmethod
    def check_format(self, file: BinaryIO) -> bool:
        pass

    @abstractmethod
    def type(self) -> KnownFormat:
        pass


def check_compare(file: BinaryIO, signature: str) -> bool:
    signature = bytes.fromhex(signature.lower())
    if rest_read_bytes(file, len(signature)) == signature:
        return True

    return False

def rest_read_bytes(file: BinaryIO, n: int) -> bytes:
    reset_stream(file)
    return file.read(n)

def reset_stream(file: BinaryIO) -> None:
    file.seek(0, os.SEEK_SET)
