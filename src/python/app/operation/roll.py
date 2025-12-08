from argparse import ArgumentParser, Namespace
from typing import final

import numpy as np

from app.image.image import Image
from app.operation.operation import Operation


@final
class RollOperation(Operation):

    @classmethod
    def name(cls) -> str:
        return 'roll'

    @classmethod
    def help(cls) -> str:
        return 'Perform data roll on given axes'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> None:
        parser.add_argument('--vertical-shift',
                            default=0,
                            dest='ver_shift',
                            type=int)
        parser.add_argument('--horizontal-shift',
                            default=0,
                            dest='hor_shift',
                            type=int)

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
