import pytest
from email.message import EmailMessage, Message
from unittest import mock

from mailers import Encrypter, InMemoryTransport, Mailer, SentMessage, Signer, Transport
from mailers.message import Email


@pytest.mark.asyncio
async def test_mailer_send(mailer, mailbox):
    message = Email(to="root@localhost", subject="SUBJECT", from_address='noreply@localhost', text='Test message.')
    await mailer.send(message)
    assert len(mailbox) == 1
    assert mailbox[0]['Subject'] == 'SUBJECT'
    assert mailbox[0]['To'] == 'root@localhost'
    assert mailbox[0]['From'] == 'noreply@localhost'


def test_mailer_send_sync(mailer, mailbox):
    message = Email(to="root@localhost", subject="SUBJECT", from_address='noreply@localhost', text='Test message.')
    mailer.send_sync(message)
    assert len(mailbox) == 1
    assert mailbox[0]['Subject'] == 'SUBJECT'
    assert mailbox[0]['To'] == 'root@localhost'
    assert mailbox[0]['From'] == 'noreply@localhost'


@pytest.mark.asyncio
async def test_mailer_sends_mime_message(mailer, mailbox):
    email = EmailMessage()
    email['Subject'] = 'SUBJECT'
    email['To'] = 'root@localhost'
    email['From'] = 'noreply@localhost'
    await mailer.send(email)
    assert len(mailbox) == 1
    assert mailbox[0]['Subject'] == 'SUBJECT'
    assert mailbox[0]['To'] == 'root@localhost'
    assert mailbox[0]['From'] == 'noreply@localhost'


class _FailingTransport(Transport):
    def __init__(self):
        self.spy = mock.MagicMock()

    async def send(self, message: Message) -> SentMessage:
        self.spy(message)
        return SentMessage(False, message, self)


@pytest.mark.asyncio
async def test_mailer_fails_to_deliver():
    failing_transport = _FailingTransport()

    message = Email(to="root@localhost", subject="SUBJECT", from_address='noreply@localhost', text='Test message.')
    mailer = Mailer(failing_transport)
    assert not await mailer.send(message)


@pytest.mark.asyncio
async def test_mailer_iterates_transports():
    mailbox = []
    failing_transport = _FailingTransport()
    memory_transport = InMemoryTransport(mailbox)

    message = Email(to="root@localhost", subject="SUBJECT", from_address='noreply@localhost', text='Test message.')
    mailer = Mailer([failing_transport, memory_transport])
    result = await mailer.send(message)
    assert len(result) == 2
    assert mailbox[0]['Subject'] == 'SUBJECT'


@pytest.mark.asyncio
async def test_mailer_iterates_transports_stops_on_first_ok():
    mailbox = []
    failing_transport = _FailingTransport()
    memory_transport = InMemoryTransport(mailbox)

    message = Email(to="root@localhost", subject="SUBJECT", from_address='noreply@localhost', text='Test message.')
    mailer = Mailer([memory_transport, failing_transport])
    result = await mailer.send(message)
    assert len(result) == 1
    assert mailbox[0]['Subject'] == 'SUBJECT'


@pytest.mark.asyncio
async def test_mailer_calls_signer():
    class _Signer(Signer):
        spy = mock.MagicMock()

        def sign(self, message: Message) -> Message:
            self.spy(message)
            return message

    mailbox = []
    memory_transport = InMemoryTransport(mailbox)
    signer = _Signer()

    message = Email(to="root@localhost", subject="SUBJECT", from_address='noreply@localhost', text='Test message.')
    mailer = Mailer(memory_transport, signer=signer)
    await mailer.send(message)
    signer.spy.assert_called_once()


@pytest.mark.asyncio
async def test_mailer_calls_encryptor():
    class _Encrypter(Encrypter):
        spy = mock.MagicMock()

        def encrypt(self, message: Message) -> Message:
            self.spy(message)
            return message

    mailbox = []
    memory_transport = InMemoryTransport(mailbox)
    encrypter = _Encrypter()

    message = Email(to="root@localhost", subject="SUBJECT", from_address='noreply@localhost', text='Test message.')
    mailer = Mailer(memory_transport, encrypter=encrypter)
    await mailer.send(message)
    encrypter.spy.assert_called_once()
