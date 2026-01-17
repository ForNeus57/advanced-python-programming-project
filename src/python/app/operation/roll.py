"""Module providing vertical or horizonal shift of the image"""

from argparse import ArgumentParser, Namespace
from typing import final, override

import numpy as np

from app.image.image import Image
from app.operation.ioperation import IOperation


@final
class Roll(IOperation):
    """Performs vertical or horizontal shift in pixels on the image"""

    @classmethod
    def name(cls) -> str:
        return 'roll'

    @classmethod
    def help(cls) -> str:
        return 'Perform data roll on given axes'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> None:
        parser.add_argument('--vertical',
                            default=0,
                            dest='ver_shift',
                            type=int)
        parser.add_argument('--horizontal',
                            default=0,
                            dest='hor_shift',
                            type=int)

    @override
    def __call__(self, args: Namespace, input_image: Image) -> Image:
        return Image(data=np.roll(
            np.roll(
                input_image.data,
                shift=args.ver_shift,
                axis=0
            ),
            shift=args.hor_shift,
            axis=1
        ))
