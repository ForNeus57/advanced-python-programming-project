from abc import ABC, abstractmethod
from argparse import Namespace, ArgumentParser


class CmdCommand(ABC):

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def help(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def parser(cls, parser: ArgumentParser) -> str:
        pass

    @abstractmethod
    def __call__(self, args: Namespace) -> None:
        pass

