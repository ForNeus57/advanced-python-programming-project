from argparse import ArgumentParser, Namespace

from app.cmd.cmd_command import CmdCommand


class ScaleCommand(CmdCommand):

    @classmethod
    def name(cls) -> str:
        return 'scale'

    @classmethod
    def help(cls) -> str:
        return 'Scale the image'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> str:
        pass

    def __call__(self, args: Namespace) -> None:
        pass
