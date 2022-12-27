import pytest
import sys

from mailers import FileTransport, InMemoryTransport, NullTransport, SMTPTransport, create_transport_from_url
from mailers.exceptions import NotRegisteredTransportError
from mailers.transports import ConsoleTransport


def test_raises_when_no_transport() -> None:
    with pytest.raises(NotRegisteredTransportError, match="for protocol 'invalid'"):
        create_transport_from_url("invalid://")


@pytest.mark.asyncio
async def test_console_transport_from_url() -> None:
    transport = create_transport_from_url("console://?stream=stdout")
    assert isinstance(transport, ConsoleTransport)
    assert transport.stream == sys.stdout


@pytest.mark.asyncio
async def test_file_transport_from_url() -> None:
    transport = create_transport_from_url("file:///tmp")
    assert isinstance(transport, FileTransport)
    assert transport.directory == "/tmp"

    with pytest.raises(ValueError, match='Argument "path" of FileTransport cannot be None.'):
        create_transport_from_url("file://")


@pytest.mark.asyncio
async def test_memory_transport_from_url() -> None:
    transport = create_transport_from_url("memory://")
    assert isinstance(transport, InMemoryTransport)


@pytest.mark.asyncio
async def test_null_transport_from_url() -> None:
    transport = create_transport_from_url("null://")
    assert isinstance(transport, NullTransport)


@pytest.mark.asyncio
async def test_smtp_transport_from_url() -> None:
    transport = create_transport_from_url("smtp://?timeout=1")
    assert isinstance(transport, SMTPTransport)
