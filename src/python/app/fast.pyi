"""Stub module for typehint of fast extension"""

import numpy as np
import numpy.typing as npt


def encode_jpeg(input_array: npt.NDArray[np.uint8]) -> bytes:   # pylint: disable=unused-argument
    """Encodes the numpy array data as jpeg image. Returns bytes that form a jpeg image."""


def decode_jpeg(input_data: bytes) -> npt.NDArray[np.uint8]:    # pylint: disable=unused-argument
    """Decodes the bytes as a JPEG image and returns the numpy array of the underlying data."""
