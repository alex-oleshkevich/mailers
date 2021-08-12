import pytest

from mailers import (
    BaseTransport,
    EmailMessage,
    NullTransport,
    add_protocol_handler,
    create_mailer,
    create_transport_from_url,
)
from mailers.exceptions import NotRegisteredTransportError


class _DummyTransport(BaseTransport):
    async def send(self, message: EmailMessage) -> None:
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
    assert isinstance(mailer.transport, NullTransport)
