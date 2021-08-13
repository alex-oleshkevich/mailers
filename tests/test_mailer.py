import pytest

from mailers import EmailMessage


@pytest.mark.asyncio
async def test_mailer_send(mailer, mailbox):
    message = EmailMessage(to="root@localhost", subject="SUBJECT", from_address='noreply@localhost')
    await mailer.send(message)
    assert len(mailbox) == 1


@pytest.mark.asyncio
async def test_mailer_sends_mime_message(mailer, mailbox):
    message = EmailMessage(to="root@localhost", subject="SUBJECT", from_address='noreply@localhost')
    await mailer.send(message.to_mime_message())
    assert len(mailbox) == 1
