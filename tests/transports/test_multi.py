import pytest
from email.message import EmailMessage
from unittest import mock

from mailers import InMemoryTransport
from mailers.transports.multi import MultiDeliveryError, MultiTransport


@pytest.mark.asyncio
async def test_multi_transport(message: EmailMessage) -> None:
    channel_ok = InMemoryTransport()
    channel_fail = InMemoryTransport()

    with mock.patch.object(channel_fail, "send", side_effect=ValueError):
        transport = MultiTransport([channel_fail, channel_ok])
        await transport.send(message)
        assert len(channel_ok.storage)
        assert not len(channel_fail.storage)


@pytest.mark.asyncio
async def test_multi_transport_nothing_delivers(message: EmailMessage) -> None:
    channel_ok = InMemoryTransport()
    channel_fail = InMemoryTransport()

    with pytest.raises(MultiDeliveryError):
        with mock.patch.object(channel_ok, "send", side_effect=ValueError):
            with mock.patch.object(channel_fail, "send", side_effect=ValueError):
                transport = MultiTransport([channel_fail, channel_ok])
                await transport.send(message)
