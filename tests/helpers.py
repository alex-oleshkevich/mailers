import typing
from email.message import EmailMessage


def get_part(message: EmailMessage, index: int) -> EmailMessage:
    return typing.cast(typing.List[EmailMessage], message.get_payload())[index]
