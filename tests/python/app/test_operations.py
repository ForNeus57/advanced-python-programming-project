from argparse import Namespace
import numpy as np

from app.image.image import Image
from app.operation.bgr2rgb import BGR2RGB
from app.operation.flip import Flip
from app.operation.grayscale import Grayscale
from app.operation.rotate90 import Rotate90


def test_bgr2rgb():
    input_image = Image(np.array([
        [[10, 20, 30], [15, 25, 35], [16, 26, 36]],
        [[20, 30, 40], [21, 31, 41], [22, 32, 42]],
        [[30, 40, 50], [31, 41, 51], [32, 42, 52]]
    ]))

    expected_image = Image(np.array([
        [[30, 20, 10], [35, 25, 15], [36, 26, 16]],
        [[40, 30, 20], [41, 31, 21], [42, 32, 22]],
        [[50, 40, 30], [51, 41, 31], [52, 42, 32]]
    ]))

    output_image = BGR2RGB()(args=None, input_image=input_image)

    assert (output_image.data == expected_image.data).all()


def test_flip():
    input_image = Image(np.array([
        [[10, 20, 30], [15, 25, 35], [16, 26, 36]],
        [[20, 30, 40], [21, 31, 41], [22, 32, 42]],
        [[30, 40, 50], [31, 41, 51], [32, 42, 52]]
    ]))

    expected_image = Image(np.array([
        [[32, 42, 52], [31, 41, 51], [30, 40, 50]],
        [[22, 32, 42], [21, 31, 41], [20, 30, 40]],
        [[16, 26, 36], [15, 25, 35], [10, 20, 30]],
    ]))

    output_image = Flip()(args=Namespace(horizontal=True, vertical=True), input_image=input_image)

    assert (expected_image.data == output_image.data).all()


def test_grayscale():
    # Try for already grayscale image
    input_image = Image(np.array([
        [[5], [123], [123]],
        [[12], [12], [12]],
        [[12], [12], [12]]
    ]))
    expected_output = input_image

    output_image = Grayscale()(args=None, input_image=input_image)

    assert (expected_output.data == output_image.data).all()

    # Try for coloured image
    input_image = Image(np.array([
        [[15, 10, 12], [120, 33, 20]],
        [[30, 0, 2], [10, 45, 22]]
    ]))

    output_image = Grayscale()(args=None, input_image=input_image)

    assert output_image.data.shape[-1] == 3
    for row in output_image.data:
        for pixel in row:
            assert np.all(pixel == pixel[0])


def test_rotate90():
    input_image = Image(np.array([
        [[15, 10, 12], [120, 33, 20]],
        [[30, 0, 2], [10, 45, 22]]
    ]))

    for rotation in range(-5, 5):
        expected_output = np.rot90(input_image.data, rotation)
        output_image = Rotate90()(args=Namespace(rotations=rotation), input_image=input_image)
        assert (expected_output == output_image.data).all()
