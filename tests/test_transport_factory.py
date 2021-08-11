import pytest

from mailers import BaseTransport, EmailMessage, add_protocol_handler
from mailers.exceptions import NotRegisteredTransportError
from mailers.transports import create_from_url


class _DummyTransport(BaseTransport):
    async def send(self, message: EmailMessage) -> None:
        pass


def test_protocol_handlers():
    add_protocol_handler('dummy', _DummyTransport)
    assert type(create_from_url('dummy://')) == _DummyTransport


def test_raises_when_no_transport():
    with pytest.raises(NotRegisteredTransportError) as ex:
        create_from_url("invalid://")
    assert str(ex.value) == 'No transport found with scheme "invalid".'
