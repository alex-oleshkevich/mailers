import pytest
import typing
from aiosmtpd.controller import Controller
from email.message import EmailMessage

from mailers import SMTPTransport


@pytest.mark.asyncio
async def test_smtp_transport(
    message: EmailMessage, smtpd_server: Controller, mailbox: typing.List[EmailMessage]
) -> None:
    backend = SMTPTransport(smtpd_server.hostname, smtpd_server.port, timeout=1)
    await backend.send(message)
    assert len(mailbox) == 1
