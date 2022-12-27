import pytest
import typing
from email.message import EmailMessage

from mailers import InMemoryTransport


@pytest.mark.asyncio
async def test_in_memory_transport(message: EmailMessage) -> None:
    storage: typing.List[EmailMessage] = []
    backend = InMemoryTransport(storage)
    await backend.send(message)
    assert len(storage) == 1
    assert backend.mailbox == storage
    assert len(backend.mailbox) == 1
