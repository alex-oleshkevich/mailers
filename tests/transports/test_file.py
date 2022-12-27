import os
import pytest
import tempfile
from email.message import EmailMessage

from mailers import FileTransport


@pytest.mark.asyncio
async def test_file_transport(message: EmailMessage) -> None:
    tmpdir = tempfile.TemporaryDirectory()
    with tmpdir as directory:
        backend = FileTransport(directory)
        await backend.send(message)

        files = os.listdir(directory)
        assert len(files) == 1
