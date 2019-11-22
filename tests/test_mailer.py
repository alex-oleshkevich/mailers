import pytest

from mailers.exceptions import NotRegisteredTransportError
from mailers.mailer import Mailer
from mailers.message import EmailMessage
from mailers.transports import EmailURL, NullTransport


def test_mailer_from_url():
    mailer = Mailer(EmailURL("null://"))
    assert isinstance(mailer._transport, NullTransport)


def test_mailer_from_transport():
    mailer = Mailer(NullTransport())
    assert isinstance(mailer._transport, NullTransport)


def test_mailer_from_string():
    mailer = Mailer("null://")
    assert isinstance(mailer._transport, NullTransport)


def test_creates_transport_raises():
    with pytest.raises(NotRegisteredTransportError) as ex:
        Mailer("invalid://")
    assert str(ex.value) == 'No transport found with scheme "invalid".'


@pytest.mark.asyncio
async def test_mailer_send(mailer, mailbox):
    message = EmailMessage(to="root@localhost", subject="SUBJECT")
    await mailer.send(message)
    assert len(mailbox) == 1
