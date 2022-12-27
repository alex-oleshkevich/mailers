import typing
from email.message import EmailMessage

from mailers import create_transport_from_url
from mailers.encrypters import Encrypter
from mailers.exceptions import DeliveryError, InvalidSenderError
from mailers.message import Email, Recipients
from mailers.plugins import Plugin
from mailers.signers import Signer
from mailers.transports import Transport

if typing.TYPE_CHECKING:
    import jinja2
else:
    try:
        import jinja2
    except ImportError:
        jinja2 = None


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

    async def send_message(
        self,
        to: Recipients,
        subject: str,
        text: typing.Any = None,
        html: typing.Any = None,
        from_address: typing.Optional[Recipients] = None,
        cc: typing.Optional[Recipients] = None,
        bcc: typing.Optional[Recipients] = None,
        reply_to: typing.Optional[Recipients] = None,
        headers: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        sender: typing.Optional[str] = None,
        return_path: typing.Optional[str] = None,
        message_id: typing.Optional[str] = None,
    ) -> None:
        message = Email(
            to=to,
            subject=str(subject or ""),
            from_address=from_address,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
            headers=dict(headers) if headers else {},
            sender=sender,
            text=str(text) if text is not None else None,
            html=str(html) if text is not None else None,
            return_path=return_path,
            text_charset="utf-8",
            html_charset="utf-8",
            message_id=message_id,
        )
        await self.send(message)


class TemplatedMailer(Mailer):
    def __init__(
        self,
        transport: typing.Union[Transport, str],
        jinja_env: "jinja2.Environment",
        from_address: typing.Optional[str] = None,
        plugins: typing.Optional[typing.Iterable[Plugin]] = None,
        signer: typing.Optional[Signer] = None,
        encrypter: typing.Optional[Encrypter] = None,
    ) -> None:
        super().__init__(transport, from_address, plugins, signer, encrypter)
        self.jinja_env = jinja_env

    async def send_templated_message(
        self,
        to: Recipients,
        subject: str,
        text_template: typing.Optional[str] = None,
        html_template: typing.Optional[str] = None,
        template_context: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        from_address: typing.Optional[Recipients] = None,
        cc: typing.Optional[Recipients] = None,
        bcc: typing.Optional[Recipients] = None,
        reply_to: typing.Optional[Recipients] = None,
        headers: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        sender: typing.Optional[str] = None,
        return_path: typing.Optional[str] = None,
        message_id: typing.Optional[str] = None,
    ) -> None:
        assert text_template or html_template, "Either text_template or html_template must be set."
        text: typing.Optional[str] = None
        html: typing.Optional[str] = None
        if text_template:
            text = self.jinja_env.get_template(text_template).render(template_context or {})
        if html_template:
            html = self.jinja_env.get_template(html_template).render(template_context or {})

        message = Email(
            to=to,
            subject=str(subject or ""),
            from_address=from_address,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
            headers=dict(headers) if headers else {},
            sender=sender,
            text=text,
            html=html,
            return_path=return_path,
            text_charset="utf-8",
            html_charset="utf-8",
            message_id=message_id,
        )
        await self.send(message)
