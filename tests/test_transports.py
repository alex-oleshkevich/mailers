import os
import pytest
import sys
import tempfile
from unittest import mock

import mailers.transports.console
import mailers.transports.file
import mailers.transports.memory
import mailers.transports.null
import mailers.transports.smtp
import mailers.transports.stream
from mailers.config import EmailURL


@pytest.mark.asyncio
async def test_null_transport(message):
    # should create from EmailURL
    backend = mailers.transports.null.NullTransport.from_url(EmailURL("null://"))
    assert isinstance(backend, mailers.transports.null.NullTransport)

    # should create from URL string
    backend = mailers.transports.null.NullTransport.from_url("null://")
    assert isinstance(backend, mailers.transports.null.NullTransport)

    backend = mailers.transports.null.NullTransport()
    await backend.send(message)


@pytest.mark.asyncio
async def test_in_memory_transport(message):
    # should create from EmailURL
    backend = mailers.transports.memory.InMemoryTransport.from_url(EmailURL("memory://"))
    assert isinstance(backend, mailers.transports.memory.InMemoryTransport)

    # should create from URL string
    backend = mailers.transports.memory.InMemoryTransport.from_url("memory://")
    assert isinstance(backend, mailers.transports.memory.InMemoryTransport)

    storage = []
    backend = mailers.transports.memory.InMemoryTransport(storage)
    await backend.send(message)
    assert len(storage) == 1
    assert backend.mailbox == storage
    assert len(backend.mailbox) == 1


@pytest.mark.asyncio
async def test_file_transport(message):
    # should create from EmailURL
    backend = mailers.transports.file.FileTransport.from_url(EmailURL("file:///tmp"))
    assert isinstance(backend, mailers.transports.file.FileTransport)

    # should create from URL string
    backend = mailers.transports.file.FileTransport.from_url("file:///tmp")
    assert isinstance(backend, mailers.transports.file.FileTransport)

    # URL must have path parameter
    with pytest.raises(ValueError) as ex:
        url = EmailURL("file://")
        mailers.transports.file.FileTransport.from_url(url)
    assert str(ex.value) == 'Argument "path" of FileTransport cannot be None.'

    tmpdir = tempfile.TemporaryDirectory()
    with tmpdir as directory:
        backend = mailers.transports.file.FileTransport(directory)
        await backend.send(message)

        files = os.listdir(directory)
        assert len(files) == 1


@pytest.mark.asyncio
async def test_smtp_transport(message, smtpd_server, mailbox):
    # should create from EmailURL
    backend = mailers.transports.smtp.SMTPTransport.from_url(EmailURL("smtp://?timeout=1"))
    assert isinstance(backend, mailers.transports.smtp.SMTPTransport)

    # should create from URL string
    backend = mailers.transports.smtp.SMTPTransport.from_url("smtp://")
    assert isinstance(backend, mailers.transports.smtp.SMTPTransport)

    backend = mailers.transports.smtp.SMTPTransport(smtpd_server.hostname, smtpd_server.port, timeout=1)
    await backend.send(message)
    assert len(mailbox) == 1


@pytest.mark.asyncio
async def test_stream_transport(message):
    class _stream:
        contents = None

        def write(self, contents):
            self.contents = contents

    stream = _stream()

    backend = mailers.transports.stream.StreamTransport(stream)
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
        backend = mailers.transports.console.ConsoleTransport('stderr')
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
        backend = mailers.transports.console.ConsoleTransport('stdout')
        await backend.send(message)
        assert len(stream.contents) == len(str(message))


@pytest.mark.asyncio
async def test_console_transport_unsupported():
    with pytest.raises(AssertionError) as ex:
        mailers.transports.console.ConsoleTransport('unknown')
    assert str(ex.value) == 'Unsupported console stream type: unknown.'


@pytest.mark.asyncio
async def test_console_transport_from_url():
    transport = mailers.transports.console.ConsoleTransport.from_url('console://?stream=stdout')
    assert transport._output == sys.stdout
