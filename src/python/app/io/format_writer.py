from abc import ABC, abstractmethod
from typing import BinaryIO

from app.image.image import Image


class FormatWriter(ABC):

    @abstractmethod
    def write_format(self, file: BinaryIO, input_image: Image) -> None:
        pass
