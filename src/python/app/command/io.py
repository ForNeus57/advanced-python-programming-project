"""Module for input/output operations related to parsing commandline"""

from sys import stdin, stdout
from typing import BinaryIO


def map_input(input_source: str) -> BinaryIO:
    """Maps input source to stdin or to the file path"""

    if input_source is None:
        return stdin.buffer

    return open(input_source, mode='rb')


def map_output(output_source: str) -> BinaryIO:
    """Maps output source to stdout or to the file path"""

    if output_source is None:
        return stdout.buffer

    return open(output_source, mode='wb')
