"""Module providing implementation of the Grayscale operation"""

from argparse import Namespace, ArgumentParser
from typing import final, override

import numpy as np

from app.image.image import Image
from app.operation.ioperation import IOperation


@final
class Grayscale(IOperation):
    """Implements the grayscale operation, does nothing on grey images"""

    @classmethod
    def name(cls) -> str:
        return 'grayscale'

    @classmethod
    def help(cls) -> str:
        return 'Converts the image to grayscale'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> None:
        pass

    @override
    def __call__(self, args: Namespace, input_image: Image) -> Image:
        if input_image.data.shape[-1] == 1:
            return input_image

        result_image = 0.2126 * input_image.data[:, :, 0] \
                     + 0.7152 * input_image.data[:, :, 1] \
                     + 0.0722 * input_image.data[:, :, 2]

        return Image(data=np.repeat(a=np.expand_dims(a=np.clip(a=result_image,
                                                               a_min=0.,
                                                               a_max=255.).astype(np.uint8),
                                                     axis=-1),
                                    repeats=3,
                                    axis=-1))
