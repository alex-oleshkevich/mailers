from typing import Any
from unittest import mock

import pytest

from mailers import EmailMessage, Mailer, configure, get_mailer, send_mail


@pytest.fixture()
def message():
    return EmailMessage()


@pytest.mark.asyncio
async def test_sends_mail(mailer, mailbox, message):
    await send_mail("root@localhost", message)
    assert message in mailbox
    assert mailbox[0].to == message.to


@pytest.mark.asyncio
async def test_send_mail_uses_mailer_by_string(message):
    spy = mock.MagicMock()

    class _mailer:
        async def send(self, message: EmailMessage) -> Any:
            spy(message)

    mailer = _mailer()

    configure(mailers={"custom": mailer})

    await send_mail("root@localhost", message, "custom")
    spy.assert_called_once_with(message)


def test_get_mailer():
    sample_mailer = object()
    default_mailer = object()
    configure(mailers={"default": default_mailer, "sample": sample_mailer})

    assert get_mailer() == default_mailer
    assert get_mailer("sample") == sample_mailer
