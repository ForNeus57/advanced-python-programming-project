from argparse import Namespace, ArgumentParser
from typing import final

from app.image.image import Image
from app.operation.operation import Operation


@final
class IdentityOperation(Operation):

    @classmethod
    def name(cls) -> str:
        return 'identity'

    @classmethod
    def help(cls) -> str:
        return 'Perform no operation on the image'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> None:
        pass

    def __call__(self, args: Namespace, input_image: Image) -> Image:
        return input_image
