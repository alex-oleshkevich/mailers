import typing as t

from .message import EmailMessage
from .transports import Transport


class Mailer:
    """A facade for sending mails."""

    def __init__(self, transport: Transport) -> None:
        self.transport = transport

    async def send(self, message: EmailMessage) -> t.Any:
        return await self.transport.send(message)


_mailers: t.Dict[str, Mailer] = {}
