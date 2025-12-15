"""Module that implements the Flip Operation"""

from argparse import Namespace, ArgumentParser
from typing import final, override

import numpy as np

from app.image.image import Image
from app.operation.ioperation import IOperation


@final
class Flip(IOperation):
    """Class that flips the image horizontally or vertically"""

    @classmethod
    def name(cls) -> str:
        return 'flip'

    @classmethod
    def help(cls) -> str:
        return 'Flip image horizontal or vertically'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> None:
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--horizontal',
                           dest='horizontal',
                           action='store_true')
        group.add_argument('--vertical',
                           dest='vertical',
                           action='store_true')

    @override
    def __call__(self, args: Namespace, input_image: Image) -> Image:
        if args.horizontal:
            input_image = Image(np.flip(input_image.data, axis=1))

        if args.vertical:
            input_image = Image(np.flip(input_image.data, axis=0))

        if not args.horizontal and not args.vertical:
            assert False, 'unreachable'
        return input_image
