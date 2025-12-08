from argparse import Namespace, ArgumentParser
from typing import final

import numpy as np

from app.image.image import Image
from app.operation.operation import Operation


@final
class HistogramEqualizationOperation(Operation):

    @classmethod
    def name(cls) -> str:
        return 'histogram_equalization'

    @classmethod
    def help(cls) -> str:
        return 'Performs histogram equalization on the image'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> None:
        pass

    def __call__(self, args: Namespace, input_image: Image) -> Image:
        output_image = np.empty_like(input_image.data)

        output_image[:, :, 0] = self.equalize_chanel(input_image.data[:, :, 0])
        output_image[:, :, 1] = self.equalize_chanel(input_image.data[:, :, 1])
        output_image[:, :, 2] = self.equalize_chanel(input_image.data[:, :, 2])

        return Image(data=output_image)

    def equalize_chanel(self, image: np.ndarray) -> np.ndarray:
        image_histogram, bins = np.histogram(image.flatten(), 256, density=True)
        cdf = image_histogram.cumsum()
        cdf = (256 - 1) * cdf / cdf[-1]

        image_equalized = np.interp(image.flatten(), bins[:-1], cdf)
        return image_equalized.reshape(image.shape)