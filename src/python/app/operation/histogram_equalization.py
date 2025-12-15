"""Module that performs histogram equalisation operation"""

from argparse import Namespace, ArgumentParser
from typing import final, override

import numpy as np

from app.image.image import Image
from app.operation.ioperation import IOperation


@final
class HistogramEqualization(IOperation):
    """Class that performs histogram equalisation on the image"""

    @classmethod
    def name(cls) -> str:
        return 'histogram_equalization'

    @classmethod
    def help(cls) -> str:
        return 'Performs histogram equalization on the image'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> None:
        pass

    @override
    def __call__(self, args: Namespace, input_image: Image) -> Image:
        output_image = np.empty_like(input_image.data)

        for channel in range(input_image.data.shape[-1]):
            output_image[:, :, channel] = self.equalize_chanel(input_image.data[:, :, channel])

        return Image(data=output_image)

    @staticmethod
    def equalize_chanel(image: np.ndarray) -> np.ndarray:
        """This method performs histogram equalisation on one input channel of the image"""

        image_histogram, bins = np.histogram(image.flatten(), 256, density=True)
        cdf = image_histogram.cumsum()
        cdf = (256 - 1) * cdf / cdf[-1]

        image_equalized = np.interp(image.flatten(), bins[:-1], cdf)
        return image_equalized.reshape(image.shape)
