"""Module providing invalid format exception"""

from app.error.app_exception import AppException


class InvalidFormatException(AppException):
    """Class that signals that the format is known, but the is some error in the binary related to the image"""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message
