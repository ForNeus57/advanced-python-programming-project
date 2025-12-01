from argparse import ArgumentParser

from app.cmd.command import CmdCommand
from app.cmd.rotate import RotateCommand


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='PROG',
                            description='Image CLI that performs different image operations like scaling, rotating etc')

    subparser = parser.add_subparsers(title='command',
                                      required=True,
                                      help='Command to be performed on an image')

    command_class: type[CmdCommand]
    for command_class in [RotateCommand]:
        command = command_class()
        parser = subparser.add_parser(name=command_class.name(),
                                      help=command_class.help())
        parser.set_defaults(func=command.__call__)

    return parser
