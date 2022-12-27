import pytest
from email.message import EmailMessage

from mailers import NullTransport


@pytest.mark.asyncio
async def test_null_transport(message: EmailMessage) -> None:
    backend = NullTransport()
    await backend.send(message)
