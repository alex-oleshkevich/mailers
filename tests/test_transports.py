import os
import sys
import tempfile
from unittest import mock

import pytest

from mailers import transports
from mailers.config import EmailURL
from mailers.exceptions import DependencyNotFound


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

    tmpdir = tempfile.TemporaryDirectory()
    with tmpdir as directory:
        backend = transports.FileTransport(directory)
        await backend.send(message)

        files = os.listdir(directory)
        assert len(files) == 1

        with mock.patch("mailers.transports.aiofiles", None):
            with pytest.raises(DependencyNotFound) as ex:
                transports.FileTransport(directory)
            assert (
                str(ex.value) == 'FileTransport requires "aiofiles" library installed.'
            )


@pytest.mark.asyncio
async def test_smtp_transport(message, smtpd_server, mailbox):
    # should create from EmailURL
    backend = transports.SMTPTransport.from_url(EmailURL("smtp://?timeout=1"))
    assert isinstance(backend, transports.SMTPTransport)

    # should create from URL string
    backend = transports.SMTPTransport.from_url("smtp://")
    assert isinstance(backend, transports.SMTPTransport)

    backend = transports.SMTPTransport(
        smtpd_server.hostname, smtpd_server.port, timeout=1
    )
    await backend.send(message)
    assert len(mailbox) == 1

    with mock.patch("mailers.transports.aiosmtplib", None):
        with pytest.raises(DependencyNotFound) as ex:
            transports.SMTPTransport(
                smtpd_server.hostname, smtpd_server.port, timeout=1
            )
        assert str(ex.value) == 'SMTPTransport requires "aiosmtplib" library installed.'


@pytest.mark.asyncio
async def test_stream_transport(message, smtpd_server, mailbox):
    class _stream:
        contents = None

        def write(self, contents):
            self.contents = contents

    stream = _stream()

    backend = transports.StreamTransport(stream)
    await backend.send(message)
    assert len(stream.contents) == len(str(message))


@pytest.mark.asyncio
async def test_console_transport(message, smtpd_server, mailbox):
    class _stream:
        contents = None

        def write(self, contents):
            self.contents = contents

    stream = _stream()

    with mock.patch.object(sys, "stdout", stream):
        backend = transports.ConsoleTransport()
        await backend.send(message)
        assert len(stream.contents) == len(str(message))


@pytest.mark.asyncio
async def test_gmail_transport(message, smtpd_server, mailbox):
    # should create from EmailURL
    backend = transports.GMailTransport.from_url(EmailURL("gmail://username:password"))
    assert isinstance(backend, transports.GMailTransport)

    # should create from URL string
    backend = transports.GMailTransport.from_url("gmail://username:password")
    assert isinstance(backend, transports.GMailTransport)

    backend = transports.GMailTransport("username", "password", timeout=1)
    assert backend._host == "smtp.gmail.com"
    assert backend._port == 465
    assert backend._use_tls is True
    assert backend._user == "username"
    assert backend._password == "password"


@pytest.mark.asyncio
async def test_mailgun_transport(message, smtpd_server, mailbox):
    # should create from EmailURL
    backend = transports.MailgunTransport.from_url(
        EmailURL("mailgun://username:password")
    )
    assert isinstance(backend, transports.MailgunTransport)

    # should create from URL string
    backend = transports.MailgunTransport.from_url("mailgun://username:password")
    assert isinstance(backend, transports.MailgunTransport)

    backend = transports.MailgunTransport("username", "password", timeout=1)
    assert backend._host == "smtp.mailgun.org"
    assert backend._port == 465
    assert backend._use_tls is True
    assert backend._user == "username"
    assert backend._password == "password"
