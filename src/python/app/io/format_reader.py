"""Module providing deserialization interface for binary streams"""

from abc import abstractmethod, ABC
from typing import BinaryIO

from app.image.image import Image


class IFormatReader(ABC):   # pylint: disable=too-few-public-methods
    """Interface that helps to deserialize image formats"""

    @abstractmethod
    def read_format(self, file: BinaryIO) -> Image:
        """Abstract method that deserialize image to binary stream"""
