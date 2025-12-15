"""Module that provides commandline Operation abstract class"""

from abc import ABC, abstractmethod
from argparse import Namespace, ArgumentParser

from app.image.image import Image


class IOperation(ABC):
    """Abstract class implementing Operation interface"""

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Abstract method that initialises the commandline name of the operation"""

    @classmethod
    @abstractmethod
    def help(cls) -> str:
        """Abstract method that initialises the commandline help message of the operation"""

    @classmethod
    @abstractmethod
    def parser(cls, parser: ArgumentParser) -> None:
        """Abstract method that initialises subcommand argument parser"""

    @abstractmethod
    def __call__(self, args: Namespace, input_image: Image) -> Image:
        pass
