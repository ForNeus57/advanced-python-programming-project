"""Module providing BGR to RGB converter"""

from argparse import Namespace, ArgumentParser
from typing import final, override

from app.image.image import Image
from app.operation.ioperation import IOperation


@final
class BGR2RGB(IOperation):
    """Converts the Blue, Green, Red channelled image to Red, Green, Blue, does nothing for grayscale iamges"""

    @classmethod
    def name(cls) -> str:
        return 'bgr2rgb'

    @classmethod
    def help(cls) -> str:
        return 'Converts the image from bgr to rgb'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> None:
        pass

    @override
    def __call__(self, args: Namespace, input_image: Image) -> Image:
        return Image(input_image.data[:, :, ::-1])
