"""Module providing unknown format exception"""

from app.error.app_exception import AppException


class UnknownFormatException(AppException):
    """The image is provided in unsupported format"""

    def __init__(self, data_format: str) -> None:
        self.data_format = data_format

    def __str__(self) -> str:
        return f'unknown data format provided: {self.data_format}'
