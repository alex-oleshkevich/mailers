import os
import pytest
import sys
import tempfile
from unittest import mock

from mailers import transports
from mailers.config import EmailURL


@pytest.mark.asyncio
async def test_null_transport(message):
    # should create from EmailURL
    backend = transports.NullTransport.from_url(EmailURL("null://"))
    assert isinstance(backend, transports.NullTransport)

    # should create from URL string
    backend = transports.NullTransport.from_url("null://")
    assert isinstance(backend, transports.NullTransport)

    backend = transports.NullTransport()
    await backend.send(message)


@pytest.mark.asyncio
async def test_in_memory_transport(message):
    # should create from EmailURL
    backend = transports.InMemoryTransport.from_url(EmailURL("memory://"))
    assert isinstance(backend, transports.InMemoryTransport)

    # should create from URL string
    backend = transports.InMemoryTransport.from_url("memory://")
    assert isinstance(backend, transports.InMemoryTransport)

    storage = []
    backend = transports.InMemoryTransport(storage)
    await backend.send(message)
    assert len(storage) == 1
    assert backend.mailbox == storage
    assert len(backend.mailbox) == 1


@pytest.mark.asyncio
async def test_file_transport(message):
    # should create from EmailURL
    backend = transports.FileTransport.from_url(EmailURL("file:///tmp"))
    assert isinstance(backend, transports.FileTransport)

    # should create from URL string
    backend = transports.FileTransport.from_url("file:///tmp")
    assert isinstance(backend, transports.FileTransport)

    # URL must have path parameter
    with pytest.raises(ValueError) as ex:
        url = EmailURL("file://")
        transports.FileTransport.from_url(url)
    assert str(ex.value) == 'Argument "path" of FileTransport cannot be None.'

    tmpdir = tempfile.TemporaryDirectory()
    with tmpdir as directory:
        backend = transports.FileTransport(directory)
        await backend.send(message)

        files = os.listdir(directory)
        assert len(files) == 1


@pytest.mark.asyncio
async def test_smtp_transport(message, smtpd_server, mailbox):
    # should create from EmailURL
    backend = transports.SMTPTransport.from_url(EmailURL("smtp://?timeout=1"))
    assert isinstance(backend, transports.SMTPTransport)

    # should create from URL string
    backend = transports.SMTPTransport.from_url("smtp://")
    assert isinstance(backend, transports.SMTPTransport)

    backend = transports.SMTPTransport(smtpd_server.hostname, smtpd_server.port, timeout=1)
    await backend.send(message.to_mime_message())
    assert len(mailbox) == 1


@pytest.mark.asyncio
async def test_stream_transport(message):
    class _stream:
        contents = None

        def write(self, contents):
            self.contents = contents

    stream = _stream()

    backend = transports.StreamTransport(stream)
    await backend.send(message)
    assert len(stream.contents) == len(str(message))


@pytest.mark.asyncio
async def test_console_transport_stderr(message):
    class _stream:
        contents = None

        def write(self, contents):
            self.contents = contents

    stream = _stream()

    with mock.patch.object(sys, "stderr", stream):
        backend = transports.ConsoleTransport('stderr')
        await backend.send(message)
        assert len(stream.contents) == len(str(message))


@pytest.mark.asyncio
async def test_console_transport_stdout(message):
    class _stream:
        contents = None

        def write(self, contents):
            self.contents = contents

    stream = _stream()

    with mock.patch.object(sys, "stdout", stream):
        backend = transports.ConsoleTransport('stdout')
        await backend.send(message)
        assert len(stream.contents) == len(str(message))


@pytest.mark.asyncio
async def test_console_transport_unsupported():
    with pytest.raises(AssertionError) as ex:
        transports.ConsoleTransport('unknown')
    assert str(ex.value) == 'Unsupported console stream type: unknown.'


@pytest.mark.asyncio
async def test_console_transport_from_url():
    transport = transports.ConsoleTransport.from_url('console://?stream=stdout')
    assert transport._output == sys.stdout
