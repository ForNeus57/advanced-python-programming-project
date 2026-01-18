import io

import numpy as np
import pytest

from app.image.image import Image
from app.io.bmp import BMPWriter, BMPReader


@pytest.mark.parametrize('data,expected', [
    (
        np.array([[[255, 0, 0], [0, 255, 0]], [[0, 0, 255], [255, 255, 255]]], dtype=np.uint8),
        b'BMF\x00\x00\x00\x00\x00\x00\x006\x00\x00\x00(\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x01\x00\x00\x00\xc8\x00\x00\x00\xc8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00',
    ),
    (
        np.array([[[237, 28, 36], [0, 162, 232]], [[255, 242, 0], [163, 73, 164]]], dtype=np.uint8),
        b'BMF\x00\x00\x00\x00\x00\x00\x006\x00\x00\x00(\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x01\x00\x00\x00\xc8\x00\x00\x00\xc8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xed\x1c$\x00\xa2\xe8\x00\x00\xff\xf2\x00\xa3I\xa4\x00\x00',
    ),
])
def test_writer(data: np.ndarray, expected: bytes) -> None:
    buffer = io.BytesIO()
    writer = BMPWriter()
    writer.write_format(buffer, Image(data=data))

    assert buffer.getvalue() == expected


@pytest.mark.parametrize('data', [
    np.array([[[255, 0, 0], [0, 255, 0]], [[0, 0, 255], [255, 255, 255]]], dtype=np.uint8),
    np.array([[[237, 28, 36], [0, 162, 232]], [[255, 242, 0], [163, 73, 164]]], dtype=np.uint8),
])
def test_transcoding_from_writer(data: np.ndarray) -> None:
    out_buffer = io.BytesIO()

    reader = BMPReader()
    writer = BMPWriter()
    writer.write_format(out_buffer, Image(data=data))

    assert np.all(reader.read_format(io.BytesIO(out_buffer.getvalue())).data == data)