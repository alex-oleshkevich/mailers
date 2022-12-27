import pytest
import typing
from aiosmtpd.controller import Controller
from email.message import EmailMessage
from unittest import mock

from mailers import SMTPTransport
from mailers.exceptions import DeliveryError


@pytest.mark.asyncio
async def test_smtp_transport(
    message: EmailMessage, smtpd_server: Controller, mailbox: typing.List[EmailMessage]
) -> None:
    backend = SMTPTransport(smtpd_server.hostname, smtpd_server.port, timeout=1)
    await backend.send(message)
    assert len(mailbox) == 1


@pytest.mark.asyncio
async def test_smtp_raises_delivery_error_if_delivery_fails(
    message: EmailMessage, smtpd_server: Controller, mailbox: typing.List[EmailMessage]
) -> None:
    with pytest.raises(DeliveryError, match="Failed to send email via SMTP transport"):
        with mock.patch("aiosmtplib.send", return_value=({}, "FAIL")):
            backend = SMTPTransport(smtpd_server.hostname, smtpd_server.port, timeout=1)
            await backend.send(message)
