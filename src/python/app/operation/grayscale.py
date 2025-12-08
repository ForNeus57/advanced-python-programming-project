from argparse import Namespace, ArgumentParser
from typing import final

import numpy as np

from app.image.image import Image
from app.operation.operation import Operation


@final
class GrayscaleOperation(Operation):

    @classmethod
    def name(cls) -> str:
        return 'grayscale'

    @classmethod
    def help(cls) -> str:
        return 'Converts the image to grayscale'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> None:
        pass

    def __call__(self, args: Namespace, input_image: Image) -> Image:
        return Image(np.expand_dims(np.clip(
            0.2126 * input_image.data[:, :, 0]
            + 0.7152 * input_image.data[:, :, 1]
            + 0.0722 * input_image.data[:, :, 1],
            a_min=0.,
            a_max=255.).astype(np.uint8),
            axis=-1))
