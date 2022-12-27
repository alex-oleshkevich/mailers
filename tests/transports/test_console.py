import io
import pytest
import sys
from email.message import EmailMessage
from unittest import mock

from mailers.transports import ConsoleTransport


@pytest.mark.asyncio
async def test_console_transport_stderr(message: EmailMessage) -> None:
    stream = io.StringIO()

    with mock.patch.object(sys, "stderr", stream):
        backend = ConsoleTransport("stderr")
        await backend.send(message)
        assert len(stream.getvalue()) == len(str(message))


@pytest.mark.asyncio
async def test_console_transport_stdout(message: EmailMessage) -> None:
    stream = io.StringIO()

    with mock.patch.object(sys, "stdout", stream):
        backend = ConsoleTransport("stdout")
        await backend.send(message)
        assert len(stream.getvalue()) == len(str(message))


@pytest.mark.asyncio
async def test_console_transport_unsupported() -> None:
    with pytest.raises(AssertionError) as ex:
        ConsoleTransport("unknown")  # type: ignore
    assert str(ex.value) == "Unsupported console stream type: unknown."
