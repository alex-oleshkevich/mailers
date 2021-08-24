import anyio as anyio
import typing as t
from email.message import Message

from .encrypters import Encrypter
from .message import Email
from .plugins import Plugin
from .signers import Signer
from .transports import Transport


class Mailer:
    """A facade for sending mails."""

    def __init__(
        self,
        transports: t.Union[t.Iterable[Transport], Transport],
        from_address: str = None,
        plugins: t.Iterable[Plugin] = None,
        signer: Signer = None,
        encrypter: Encrypter = None,
    ) -> None:
        if isinstance(transports, Transport):
            transports = [transports]

        self.transports = transports
        self.from_address = from_address
        self.signer = signer
        self.encrypter = encrypter
        self.plugins = plugins or []

    async def send(self, message: t.Union[Email, Message]) -> t.Any:
        mime_message = message.build() if isinstance(message, Email) else message
        for plugin in self.plugins:
            await plugin.on_before_send(mime_message)

        if self.encrypter:
            mime_message = self.encrypter.encrypt(mime_message)

        if self.signer:
            mime_message = self.signer.sign(mime_message)

        for transport in self.transports:
            try:
                await transport.send(mime_message)
            except Exception:
                raise
            else:
                break

        for plugin in self.plugins:
            await plugin.on_after_send(mime_message)

    def send_sync(self, message: t.Union[Email, Message]) -> t.Any:
        anyio.run(self.send, message)


_mailers: t.Dict[str, Mailer] = {}
