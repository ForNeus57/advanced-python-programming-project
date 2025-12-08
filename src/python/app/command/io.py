from sys import stdin, stdout
from typing import BinaryIO


def map_input(input_source: str) -> BinaryIO:
    if input_source is None:
        return stdin.buffer

    return open(input_source, mode='rb')


def map_output(output_source: str) -> BinaryIO:
    if output_source is None:
        return stdout.buffer

    return open(output_source, mode='wb')
