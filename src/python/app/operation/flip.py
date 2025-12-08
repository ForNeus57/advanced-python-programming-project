from argparse import Namespace, ArgumentParser
from typing import final

import numpy as np

from app.image.image import Image
from app.operation.operation import Operation


@final
class FlipOperation(Operation):

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

    def __call__(self, args: Namespace, input_image: Image) -> Image:
        if args.horizontal:
            return Image(np.flip(input_image.data, axis=1))

        if args.vertical:
            return Image(np.flip(input_image.data, axis=0))

        assert False, 'unreachable'
