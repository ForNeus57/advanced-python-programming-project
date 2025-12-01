from argparse import ArgumentParser, Namespace

from app.cmd.cmd_command import CmdCommand


class TranslateCommand(CmdCommand):

    @classmethod
    def name(cls) -> str:
        return 'translate'

    @classmethod
    def help(cls) -> str:
        return 'Translate the image'

    @classmethod
    def parser(cls, parser: ArgumentParser) -> str:
        pass

    def __call__(self, args: Namespace) -> None:
        pass
