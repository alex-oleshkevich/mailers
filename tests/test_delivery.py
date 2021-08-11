import pytest

from mailers import EmailMessage, send


@pytest.mark.asyncio
async def test_mailer_send(mailbox):
    message = EmailMessage(to="root@localhost", subject="SUBJECT", from_address='noreply@localhost')
    await send(message)
    assert len(mailbox) == 1
