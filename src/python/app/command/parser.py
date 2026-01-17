"""Module containing functions that provide functionality related to commandline arguments parsing"""

from argparse import ArgumentParser, Namespace
from typing import Callable

from app.command.io import map_input, map_output
from app.io.format_factory import get_reader_from_format, get_writer_from_format, determine_format
from app.io.known_format import KnownFormat
from app.operation import Rotate90, Identity, Flip, BGR2RGB, Roll, Grayscale, HistogramEqualization, IOperation


def get_parser() -> ArgumentParser:
    """Functions that initialises the Argument Parser"""

    parser = ArgumentParser(prog='PROG',
                            description='Image CLI that performs different image operations like scaling, rotating etc')
    parser.add_argument('--input', '-i',
                        nargs='?',
                        default=None,
                        dest='input',
                        help='program input')
    parser.add_argument('--output', '-o',
                        nargs='?',
                        default=None,
                        dest='output',
                        help='program output')
    parser.add_argument('--output-format',
                        nargs='?',
                        default=None,
                        choices=KnownFormat.get_available_formats(),
                        dest='output_format',
                        help='change the output stream data format')

    subparser = parser.add_subparsers(required=True,
                                      help='Command or operation to be performed on an image')

    for operation_class in available_commands():
        operation = operation_class()

        operation_parser = subparser.add_parser(name=operation_class.name(),
                                                help=operation_class.help())
        operation_parser.set_defaults(func=prepare_command(operation))

        operation_class.parser(operation_parser)

    return parser


def prepare_command(command: IOperation) -> Callable[[Namespace], int]:
    """Function that decorates the operation in order to provide input and output to it"""

    def wrapper(args: Namespace) -> int:
        with map_input(args.input) as input_source:
            data_format = determine_format(input_source)

            reader = get_reader_from_format(data_format)
            writer = get_writer_from_format(data_format
                                            if args.output_format is None
                                            else KnownFormat.from_string(args.output_format))

            input_arr = reader.read_format(input_source)
        result = command(args, input_arr)

        with map_output(args.output) as output_source:
            writer.write_format(output_source, result)

        return 0

    return wrapper


def available_commands():
    """Function that returns all the supported commandline operations by the program"""

    return [
        Rotate90,
        Identity,
        Flip,
        BGR2RGB,
        Roll,
        Grayscale,
        HistogramEqualization,
    ]
