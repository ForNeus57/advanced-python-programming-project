from argparse import ArgumentParser, Namespace
from typing import Callable

from app.command.io import map_input, map_output
from app.io.format_factory import get_reader_from_format, KnownFormat, get_writer_from_format
from app.operation.bgr2rgb import BGR2RGBOperation
from app.operation.flip import FlipOperation
from app.operation.grayscale import GrayscaleOperation
from app.operation.histogram_equalization import HistogramEqualizationOperation
from app.operation.identity import IdentityOperation
from app.operation.operation import Operation
from app.operation.roll import RollOperation

from app.operation.rotate90 import Rotate90Operation


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='PROG',
                            description='Image CLI that performs different image operations like scaling, rotating etc')
    parser.add_argument('input',
                        nargs='?',
                        default=None,
                        help='program input')
    parser.add_argument('output',
                        nargs='?',
                        default=None,
                        help='program output')
    parser.add_argument('--format',
                        nargs='?',
                        default=KnownFormat.default().name.lower(),
                        choices=KnownFormat.get_available_formats(),
                        help='program output')

    subparser = parser.add_subparsers(required=True,
                                      help='Command to be performed on an image')

    for operation_class in available_commands():
        operation = operation_class()

        operation_parser = subparser.add_parser(name=operation_class.name(),
                                                help=operation_class.help())
        operation_parser.set_defaults(func=prepare_command(operation))

        operation_class.parser(operation_parser)

    return parser


def prepare_command(command: Operation) -> Callable[[Namespace], int]:

    def wrapper(args: Namespace) -> int:
        data_format = KnownFormat.from_string(args.format)
        reader = get_reader_from_format(data_format)
        writer = get_writer_from_format(data_format)

        with map_input(args.input) as input_source, map_output(args.output) as output_source:
            input_arr = reader.read_format(input_source)
            result = command(args, input_arr)
            writer.write_format(output_source, result)

        return 0

    return wrapper


def available_commands():
    return [
        Rotate90Operation,
        IdentityOperation,
        FlipOperation,
        BGR2RGBOperation,
        RollOperation,
        GrayscaleOperation,
        HistogramEqualizationOperation,
    ]
