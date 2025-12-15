"""Module containing the clockwise rotation of the image"""

from argparse import ArgumentParser, Namespace
from typing import final, override

import numpy as np

from app.image.image import Image
from app.operation.ioperation import IOperation


@final
class Rotate90(IOperation):
    """Performs 90-degree clockwise rotation of the image"""

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
                            help='number of full rotations (clockwise), negative numbers ')

    @override
    def __call__(self, args: Namespace, input_image: Image) -> Image:
        return Image(np.rot90(input_image.data, k=args.rotations))
