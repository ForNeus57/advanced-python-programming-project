"""Module providing serialization interface for binary streams"""

from abc import ABC, abstractmethod
from typing import BinaryIO

from app.image.image import Image


class IFormatWriter(ABC):   # pylint: disable=too-few-public-methods
    """Interface that helps to serialize image formats"""

    @abstractmethod
    def write_format(self, file: BinaryIO, input_image: Image) -> None:
        """Abstract method that serializes image to binary stream"""
