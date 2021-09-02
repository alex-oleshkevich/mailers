import anyio as anyio
import typing as t
from email.message import Message

from .encrypters import Encrypter
from .exceptions import InvalidSenderError
from .message import Email
from .plugins import Plugin
from .result import SentMessages
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

    async def send(self, message: t.Union[Email, Message]) -> SentMessages:
        from_ = message.from_address if isinstance(message, Email) else message.get('From')
        sender_ = message.sender if isinstance(message, Email) else message.get('Sender')

        if not from_ and not self.from_address and not sender_:
            raise InvalidSenderError('Message must have "From" or "Sender" header.')

        if not from_ and self.from_address:
            if isinstance(message, Email):
                message.from_address = self.from_address
            else:
                message['From'] = self.from_address

        for plugin in self.plugins:
            if isinstance(message, Email):
                message = plugin.process_email(message)

        mime_message = message.build() if isinstance(message, Email) else message

        for plugin in self.plugins:
            await plugin.on_before_send(mime_message)

        if self.encrypter:
            mime_message = self.encrypter.encrypt(mime_message)

        if self.signer:
            mime_message = self.signer.sign(mime_message)

        sent_messages = SentMessages()
        for transport in self.transports:
            sent_message = await transport.send(mime_message)
            sent_messages.append(sent_message)
            if sent_message.ok:
                break

        for plugin in self.plugins:
            if sent_messages.ok:
                await plugin.on_after_send(mime_message, sent_messages)
            else:
                await plugin.on_send_error(mime_message, sent_messages)

        return sent_messages

    def send_sync(self, message: t.Union[Email, Message]) -> t.Any:
        anyio.run(self.send, message)


_mailers: t.Dict[str, Mailer] = {}
