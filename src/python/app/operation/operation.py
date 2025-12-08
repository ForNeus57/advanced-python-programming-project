from abc import ABC, abstractmethod
from argparse import Namespace, ArgumentParser
from typing import final

import numpy as np

from app.image.image import Image


class Operation(ABC):

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def help(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def parser(cls, parser: ArgumentParser) -> None:
        pass

    @abstractmethod
    def __call__(self, args: Namespace, input_image: Image) -> Image:
        pass
