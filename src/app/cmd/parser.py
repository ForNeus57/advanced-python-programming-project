from argparse import ArgumentParser

from app.cmd.cmd_command import CmdCommand
from app.cmd.rotate import RotateCommand
from app.cmd.scale import ScaleCommand
from app.cmd.translate import TranslateCommand


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='PROG',
                            description='Image CLI that performs different image operations like scaling, rotating etc')

    subparser = parser.add_subparsers(required=True,
                                      help='Command to be performed on an image')

    command_class: type[CmdCommand]
    for command_class in [RotateCommand, ScaleCommand, TranslateCommand]:
        command = command_class()

        parser = subparser.add_parser(name=command_class.name(),
                                      help=command_class.help())
        parser.set_defaults(func=command)

        command_class.parser(parser)

    return parser
