import io
import pytest
from email.message import EmailMessage

from mailers import StreamTransport


@pytest.mark.asyncio
async def test_stream_transport(message: EmailMessage) -> None:
    stream = io.StringIO("")
    backend = StreamTransport(stream)
    await backend.send(message)
    assert len(stream.getvalue()) == len(str(message))
