import pytest
import typing
from email.message import EmailMessage
from unittest import mock

from mailers import Encrypter, InMemoryTransport, Mailer, NullTransport, Signer, Transport
from mailers.exceptions import DeliveryError, InvalidSenderError
from mailers.message import Email


def test_mailer_creates_transport_from_string() -> None:
    mailer = Mailer("null://")
    assert isinstance(mailer.transport, NullTransport)


@pytest.mark.asyncio
async def test_mailer_send(mailer: Mailer, mailbox: typing.List[EmailMessage]) -> None:
    message = Email(to="root@localhost", subject="SUBJECT", from_address="noreply@localhost", text="Test message.")
    await mailer.send(message)
    assert len(mailbox) == 1
    assert mailbox[0]["Subject"] == "SUBJECT"
    assert mailbox[0]["To"] == "root@localhost"
    assert mailbox[0]["From"] == "noreply@localhost"


@pytest.mark.asyncio
async def test_mailer_send_sync(mailer: Mailer, mailbox: typing.List[EmailMessage]) -> None:
    message = Email(to="root@localhost", subject="SUBJECT", from_address="noreply@localhost", text="Test message.")
    await mailer.send(message)
    assert len(mailbox) == 1
    assert mailbox[0]["Subject"] == "SUBJECT"
    assert mailbox[0]["To"] == "root@localhost"
    assert mailbox[0]["From"] == "noreply@localhost"


@pytest.mark.asyncio
async def test_mailer_sends_mime_message(mailer: Mailer, mailbox: typing.List[EmailMessage]) -> None:
    email = EmailMessage()
    email["Subject"] = "SUBJECT"
    email["To"] = "root@localhost"
    email["From"] = "noreply@localhost"
    await mailer.send(email)
    assert len(mailbox) == 1
    assert mailbox[0]["Subject"] == "SUBJECT"
    assert mailbox[0]["To"] == "root@localhost"
    assert mailbox[0]["From"] == "noreply@localhost"


class _FailingTransport(Transport):
    def __init__(self) -> None:
        self.spy = mock.MagicMock()

    async def send(self, message: EmailMessage) -> None:
        self.spy(message)


@pytest.mark.asyncio
async def test_mailer_fails_to_deliver() -> None:
    failing_transport = _FailingTransport()

    message = Email(to="root@localhost", subject="SUBJECT", from_address="noreply@localhost", text="Test message.")
    mailer = Mailer(failing_transport)
    await mailer.send(message)


@pytest.mark.asyncio
async def test_mailer_calls_signer() -> None:
    class _Signer(Signer):
        spy = mock.MagicMock()

        def sign(self, message: EmailMessage) -> EmailMessage:
            self.spy(message)
            return message

    mailbox: typing.List[EmailMessage] = []
    memory_transport = InMemoryTransport(mailbox)
    signer = _Signer()

    message = Email(to="root@localhost", subject="SUBJECT", from_address="noreply@localhost", text="Test message.")
    mailer = Mailer(memory_transport, signer=signer)
    await mailer.send(message)
    signer.spy.assert_called_once()


@pytest.mark.asyncio
async def test_mailer_calls_encryptor() -> None:
    class _Encrypter(Encrypter):
        spy = mock.MagicMock()

        def encrypt(self, message: EmailMessage) -> EmailMessage:
            self.spy(message)
            return message

    mailbox: typing.List[EmailMessage] = []
    memory_transport = InMemoryTransport(mailbox)
    encrypter = _Encrypter()

    message = Email(to="root@localhost", subject="SUBJECT", from_address="noreply@localhost", text="Test message.")
    mailer = Mailer(memory_transport, encrypter=encrypter)
    await mailer.send(message)
    encrypter.spy.assert_called_once()


@pytest.mark.asyncio
async def test_mailer_raises_if_no_sender_and_no_from() -> None:
    """If message has no From, Sender headers and not defines a global from_address, then it must raise."""
    mailbox: typing.List[EmailMessage] = []
    memory_transport = InMemoryTransport(mailbox)
    mailer = Mailer(memory_transport)
    email = Email(text="Message")
    with pytest.raises(InvalidSenderError) as ex:
        await mailer.send(email)
    assert str(ex.value) == 'Message must have "From" or "Sender" header.'


@pytest.mark.asyncio
async def test_mailer_not_raises_if_no_sender_and_from_exists() -> None:
    """If message has no From, Sender headers and not defines a global from_address, then it must raise."""
    mailbox: typing.List[EmailMessage] = []
    memory_transport = InMemoryTransport(mailbox)
    mailer = Mailer(memory_transport)
    email = Email(text="Message", from_address="root@localhost")
    await mailer.send(email)
    assert mailbox[0]["From"] == "root@localhost"


@pytest.mark.asyncio
async def test_mailer_not_raises_if_sender_and_no_from() -> None:
    mailbox: typing.List[EmailMessage] = []
    memory_transport = InMemoryTransport(mailbox)
    mailer = Mailer(memory_transport)
    email = Email(text="Message", sender="root@localhost")
    await mailer.send(email)
    assert mailbox[0]["Sender"] == "root@localhost"


@pytest.mark.asyncio
async def test_mailer_applies_global_from_if_no_sender_and_no_from_in_message() -> None:
    mailbox: typing.List[EmailMessage] = []
    memory_transport = InMemoryTransport(mailbox)
    mailer = Mailer(memory_transport, from_address="root@localhost")
    email = Email(text="Message")
    await mailer.send(email)
    assert mailbox[0]["From"] == "root@localhost"

    mime_mail = EmailMessage()
    await mailer.send(mime_mail)
    assert mailbox[0]["From"] == "root@localhost"


@pytest.mark.asyncio
async def test_mailer_uses_from_from_message() -> None:
    mailbox: typing.List[EmailMessage] = []
    memory_transport = InMemoryTransport(mailbox)
    mailer = Mailer(memory_transport, from_address="user@localhost")
    email = Email(text="Message", from_address="root@localhost")
    await mailer.send(email)
    assert mailbox[0]["From"] == "root@localhost"


@pytest.mark.asyncio
async def test_mailer_uses_sender_from_message() -> None:
    mailbox: typing.List[EmailMessage] = []
    memory_transport = InMemoryTransport(mailbox)
    mailer = Mailer(memory_transport, from_address="user@localhost")
    email = Email(text="Message", sender="root@localhost")
    await mailer.send(email)
    assert "From" not in mailbox[0]["Sender"]
    assert mailbox[0]["Sender"] == "root@localhost"


@pytest.mark.asyncio
async def test_mailer_send_message_shortcut() -> None:
    mailbox: typing.List[EmailMessage] = []
    memory_transport = InMemoryTransport(mailbox)
    mailer = Mailer(memory_transport, from_address="user@localhost")
    await mailer.send_message(to="roo@localhost", subject="Hello", text="World")
    assert len(mailbox)


@pytest.mark.asyncio
async def test_mailer_raises_delivery_error() -> None:
    mailbox: typing.List[EmailMessage] = []
    memory_transport = InMemoryTransport(mailbox)
    with mock.patch.object(memory_transport, "send", side_effect=ValueError):
        with pytest.raises(DeliveryError, match="Failed to deliver email message"):
            mailer = Mailer(memory_transport, from_address="user@localhost")
            await mailer.send_message(to="roo@localhost", subject="Hello", text="World")
