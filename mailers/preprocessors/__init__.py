import typing
from email.message import EmailMessage


class Preprocessor(typing.Protocol):
    def __call__(self, message: EmailMessage) -> EmailMessage:
        ...
