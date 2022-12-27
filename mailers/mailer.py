import typing
from email.message import EmailMessage

from mailers import create_transport_from_url
from mailers.encrypters import Encrypter
from mailers.exceptions import DeliveryError, InvalidSenderError
from mailers.message import Email
from mailers.plugins import Plugin
from mailers.signers import Signer
from mailers.transports import Transport


class Mailer:
    """A facade for sending mails."""

    def __init__(
        self,
        transport: typing.Union[Transport, str],
        from_address: typing.Optional[str] = None,
        plugins: typing.Optional[typing.Iterable[Plugin]] = None,
        signer: typing.Optional[Signer] = None,
        encrypter: typing.Optional[Encrypter] = None,
    ) -> None:
        if isinstance(transport, str):
            transport = create_transport_from_url(transport)
        self.transport = transport
        self.from_address = from_address
        self.signer = signer
        self.encrypter = encrypter
        self.plugins = plugins or []

    async def send(self, message: typing.Union[Email, EmailMessage]) -> None:
        from_ = message.from_address if isinstance(message, Email) else message.get("From")
        sender_ = message.sender if isinstance(message, Email) else message.get("Sender")

        if not from_ and not self.from_address and not sender_:
            raise InvalidSenderError('Message must have "From" or "Sender" header.')

        if not from_ and self.from_address:
            if isinstance(message, Email):
                message.from_address = self.from_address
            else:
                message["From"] = self.from_address

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

        try:
            await self.transport.send(mime_message)
            for plugin in self.plugins:
                await plugin.on_after_send(mime_message)
        except Exception as ex:
            raise DeliveryError("Failed to deliver email message.") from ex
