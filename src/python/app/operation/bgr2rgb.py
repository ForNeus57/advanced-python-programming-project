from argparse import Namespace, ArgumentParser
from typing import final

from app.image.image import Image
from app.operation.operation import Operation


@final
class BGR2RGBOperation(Operation):

    @classmethod
    def name(cls) -> str:
        return 'bgr2rgb'

    @classmethod
    def help(cls) -> str:
        return 'Converts the image from bgr to rgb'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> None:
        pass

    def __call__(self, args: Namespace, input_image: Image) -> Image:
        return Image(input_image.data[:, :, ::-1])
