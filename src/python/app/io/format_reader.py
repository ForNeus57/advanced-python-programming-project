from abc import abstractmethod, ABC
from typing import BinaryIO

import numpy as np

from app.image.image import Image


class FormatReader(ABC):

    @abstractmethod
    def read_format(self, file: BinaryIO) -> Image:
        pass
