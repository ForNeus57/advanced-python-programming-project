from abc import abstractmethod, ABC
from argparse import Namespace


class RotateCommand(ABC):

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        return 'rotate'

    @classmethod
    @abstractmethod
    def help(cls) -> str:
        return 'Rotate the image '

    @abstractmethod
    def __call__(self, args: Namespace) -> None:
        pass