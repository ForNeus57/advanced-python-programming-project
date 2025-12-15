"""Module that implements the Identity operation"""

from argparse import Namespace, ArgumentParser
from typing import final, override

from app.image.image import Image
from app.operation.ioperation import IOperation


@final
class Identity(IOperation):
    """It is an identity operation meaning it returns the same thing that it got as an input"""

    @classmethod
    def name(cls) -> str:
        return 'identity'

    @classmethod
    def help(cls) -> str:
        return 'Perform no operation on the image'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> None:
        pass

    @override
    def __call__(self, args: Namespace, input_image: Image) -> Image:
        return input_image
