import pytest
from email.message import Message

from mailers import NullTransport, Transport, add_protocol_handler, create_mailer, create_transport_from_url
from mailers.exceptions import NotRegisteredTransportError


class _DummyTransport(Transport):  # pragma: no cover
    async def send(self, message: Message) -> None:
        pass


def test_protocol_handlers():
    add_protocol_handler('dummy', _DummyTransport)
    assert type(create_transport_from_url('dummy://')) == _DummyTransport


def test_raises_when_no_transport():
    with pytest.raises(NotRegisteredTransportError) as ex:
        create_transport_from_url("invalid://")
    assert str(ex.value) == 'No transport found with scheme "invalid".'


def test_create_mailer_from_url():
    mailer = create_mailer('null://')
    assert isinstance(mailer.transports[0], NullTransport)
