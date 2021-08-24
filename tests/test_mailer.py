import pytest
from email.message import EmailMessage

from mailers.message import Email


@pytest.mark.asyncio
async def test_mailer_send(mailer, mailbox):
    message = Email(to="root@localhost", subject="SUBJECT", from_address='noreply@localhost', text='Test message.')
    await mailer.send(message)
    assert len(mailbox) == 1
    assert mailbox[0]['Subject'] == 'SUBJECT'
    assert mailbox[0]['To'] == 'root@localhost'
    assert mailbox[0]['From'] == 'noreply@localhost'


def test_mailer_send_sync(mailer, mailbox):
    message = Email(to="root@localhost", subject="SUBJECT", from_address='noreply@localhost', text='Test message.')
    mailer.send_sync(message)
    assert len(mailbox) == 1
    assert mailbox[0]['Subject'] == 'SUBJECT'
    assert mailbox[0]['To'] == 'root@localhost'
    assert mailbox[0]['From'] == 'noreply@localhost'


@pytest.mark.asyncio
async def test_mailer_sends_mime_message(mailer, mailbox):
    email = EmailMessage()
    email['Subject'] = 'SUBJECT'
    email['To'] = 'root@localhost'
    email['From'] = 'noreply@localhost'
    await mailer.send(email)
    assert len(mailbox) == 1
    assert mailbox[0]['Subject'] == 'SUBJECT'
    assert mailbox[0]['To'] == 'root@localhost'
    assert mailbox[0]['From'] == 'noreply@localhost'
