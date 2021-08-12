import typing as t

from .message import EmailMessage
from .plugins import Plugin
from .transports import Transport


class Mailer:
    """A facade for sending mails."""

    def __init__(self, transport: Transport, plugins: t.Iterable[Plugin] = None) -> None:
        self.transport = transport
        self.plugins = plugins or []

    async def send(self, message: EmailMessage) -> t.Any:
        for plugin in self.plugins:
            await plugin.on_before_send(message)

        await self.transport.send(message)
        for plugin in self.plugins:
            await plugin.on_after_send(message)


_mailers: t.Dict[str, Mailer] = {}
