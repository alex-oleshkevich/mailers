import typing as t
from email.message import Message

from .message import EmailMessage
from .plugins import Plugin
from .transports import Transport


class Mailer:
    """A facade for sending mails."""

    def __init__(self, transport: Transport, plugins: t.Iterable[Plugin] = None) -> None:
        self.transport = transport
        self.plugins = plugins or []

    async def send(self, message: t.Union[EmailMessage, Message]) -> t.Any:
        if isinstance(message, EmailMessage):
            mime_message = message.to_mime_message()
        else:
            mime_message = message

        for plugin in self.plugins:
            await plugin.on_before_send(mime_message)

        await self.transport.send(mime_message)
        for plugin in self.plugins:
            await plugin.on_after_send(mime_message)


_mailers: t.Dict[str, Mailer] = {}
