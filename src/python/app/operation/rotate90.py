from argparse import ArgumentParser, Namespace
from typing import final

import numpy as np

from app.image.image import Image
from app.operation.operation import Operation


@final
class Rotate90Operation(Operation):

    @classmethod
    def name(cls) -> str:
        return 'rotate90'

    @classmethod
    def help(cls) -> str:
        return 'Perform 90 deg rotation'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> None:
        parser.add_argument('--rotations',
                            default=1,
                            type=int,
                            help='number of full rotations (clockwise), negative numbers '
                            )

    def __call__(self, args: Namespace, input_image: Image) -> Image:
        return Image(np.rot90(input_image.data, k=args.rotations))
